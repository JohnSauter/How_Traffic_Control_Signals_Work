Name:           How_Traffic_Control_Signals_Work
Version:        0.11
Release:        1%{?dist}
Summary:        Explain traffic control signals

License:        GPLv3+
URL:            https://github.com/JohnSauter/How_Traffic_Control_Signals_Work
Source0:        https://github.com/JohnSauter/How_Traffic_Control_Signals_Work/blob/master/How_Traffic_Control_Signals_Work-%{version}.tar.gz
                
BuildArch: noarch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  python3 >= 3.10
BuildRequires:  git
BuildRequires: graphviz
BuildRequires: inkscape
BuildRequires: texlive-scheme-full
BuildRequires: sil-andika-fonts
BuildRequires: sil-charis-fonts
BuildRequires: liberation-mono-fonts

%global _hardened_build 1

%description
Explain how traffic control signals work using finite state machines
equipped with timers, toggles to communicate with each other,
and system programs to coordinate between them.

%prep
%autosetup -S git

%build

%configure

%make_build

%install
%make_install

%check
make check VERBOSE=1

%files
%defattr(-,root,root)
%exclude /usr/share/doc/%{name}/AUTHORS
%exclude /usr/share/doc/%{name}/COPYING
%exclude /usr/share/doc/%{name}/ChangeLog
%exclude /usr/share/doc/%{name}/INSTALL
%exclude /usr/share/doc/%{name}/NEWS
%exclude /usr/share/doc/%{name}/README
%exclude /usr/share/doc/%{name}/LICENSE
%doc traffic_control_signals.pdf
%doc AUTHORS ChangeLog NEWS README
%license LICENSE
%license COPYING

%changelog
 * Sun Jan 12 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.11-1 More work on the animation.
 * Sat Jan 04 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.10-1 More work on the animation.
 * Wed Jan 01 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.9-1 Work on the animation.
 * Mon Dec 30 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.8-1 Start work on the renderer.
 * Sun Dec 29 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.7-1 Through lanes move at full speed in the intersection.
 * Wed Dec 25 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.6-1 Vehicles and pedestrians work.
 * Mon Dec 23 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.5-1 Start work on vehicles and pedestrians.
 * Sun Dec 22 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.4-1 Improve consistency of log output for make check.
 * Sat Dec 21 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.3-1 Improve overlap of green signals
 * Sun Dec 15 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.2-1 I work on it as I have time.
 * Sat Nov 30 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.1-1 Initial version.
