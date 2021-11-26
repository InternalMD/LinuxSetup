from steps.step import Step
from utils import command
import os
from utils.log import log
from enum import Enum


class FileType(Enum):
    PosixShell = 1
    XResources = 2
    Bash = 3
    Sxhkd = 4

    _properties = {
        PosixShell: ("#", "#!/usr/bin/sh"),
        XResources: ("!", None),
        Bash: ("#", "#!/usr/bin/bash"),
        Sxhkd: ("#", None),
    }

    @classmethod
    def _get_properties(cls, file_type):
        return cls._properties.value[file_type.value]

    @classmethod
    def get_comment_prefix(cls, file_type):
        return cls._get_properties(file_type)[0]

    @classmethod
    def get_shebang(cls, file_type):
        return cls._get_properties(file_type)[1]


class LinePlacement(Enum):
    Normal = 1
    End = 2


class DotFilesStep(Step):
    def __init__(self, root_dir):
        super().__init__("Dotfiles")
        self.root_dir = root_dir
        self.files_map = dict()
        self.symlinks = []
        self._setup_hardcoded_settings()

    def _setup_hardcoded_settings(self):
        self.add_dotfile_section(
            ".profile",
            "Some constants",
            [
                f"export LINUX_SETUP_ROOT={self.root_dir}",
                "export EDITOR=nano",
                "export BROWSER=chromium",
            ],
        )
        self.add_dotfile_section(
            ".profile",
            "Allow attaching debugger to a running process",
            [
                "echo 0 | sudo tee '/proc/sys/kernel/yama/ptrace_scope' > /dev/null",
            ],
        )
        self.add_dotfile_section(
            ".profile",
            "ls aliases",
            [
                "alias ls='ls --color=auto'",
                "alias ll='ls -la'",
            ],
        )

        self.add_dotfile_section(
            ".bashrc",
            "Call .profile",
            [
                "source ~/.profile",
            ],
            file_type=FileType.Bash,
            line_placement=LinePlacement.End,
        )
        self.add_dotfile_section(
            ".profile",
            "Automatically startup GUI only on tty1",
            [
                '[ -z "$DISPLAY" ] && [ "$(tty)" = /dev/tty1 ] && startx',
            ],
            line_placement=LinePlacement.End,
        )

    def _perform_impl(self):
        for dotfile, line_groups in self.files_map.items():
            with open(dotfile, "w") as file:
                lines_count = 0
                for lines in line_groups.values():
                    file.writelines((f"{x}\n" for x in lines))
                    lines_count += len(lines)
            log(f"Setting up {dotfile} with {lines_count} lines")

        for src, link in self.symlinks:
            log(f"Creating symlink {link} -> {src}")
            try:
                os.remove(link)
            except FileNotFoundError:
                pass
            os.symlink(src, link)

    def add_dotfile_lines(
        self,
        dotfile,
        lines,
        *,
        prepend_home_dir=True,
        file_type=FileType.PosixShell,
        line_placement=LinePlacement.Normal,
    ):
        if prepend_home_dir:
            dotfile = f'{os.environ["HOME"]}/{dotfile}'

        if dotfile not in self.files_map:
            prefix = FileType.get_comment_prefix(file_type)
            shebang = FileType.get_shebang(file_type)
            init_lines = []
            if shebang:
                init_lines.append(shebang)
                init_lines.append(prefix)
            init_lines += [
                f"{prefix} This file has been autogenerated by LinuxSetup.",
                f"{prefix} Do not change it manually",
                f"{prefix}",
                f"",
            ]
            self.files_map[dotfile] = {
                LinePlacement.Normal: init_lines,
                LinePlacement.End: [],
            }
        self.files_map[dotfile][line_placement] += lines

    def add_dotfile_section(self, dotfile, section_comment, lines, **kwargs):
        lines = [f"# {section_comment}"] + lines + [""]
        self.add_dotfile_lines(dotfile, lines, **kwargs)

    def add_dotfile_symlink(self, src, link, *, prepend_home_dir_src=True, prepend_home_dir_link=True):
        if prepend_home_dir_src:
            src = f'{os.environ["HOME"]}/{src}'
        if prepend_home_dir_link:
            link = f'{os.environ["HOME"]}/{link}'
        self.symlinks.append((src, link))
