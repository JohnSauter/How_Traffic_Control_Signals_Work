Name:           How_Traffic_Control_Signals_Work
Version:        2024.11.30
Release:        1%{?dist}
Summary:        Explain traffic control signals

License:        GPLv3+
URL:            https://github.com/JohnSauter/How_Traffic_Control_Signals_Work
Source0:        https://github.com/JohnSauter/How_Traffic_Control_Signals_Work/blob/master/How_Traffic_Control_Signals_Work-%{version}.tar.gz
                
BuildArch: noarch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  python3 >= 3.5
BuildRequires:  git
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

# Tell configure to rebuild the PDF file
%configure --enable-pdf

%make_build

%install
%make_install

%check
make check VERBOSE=1

%files
%defattr(-,root,root)
%doc traffic_control_signals.pdf
%doc AUTHORS ChangeLog NEWS README
%license LICENSE
%license COPYING

%changelog
 * Sat Nov 30 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 2024.11.30-1 Initial version.
