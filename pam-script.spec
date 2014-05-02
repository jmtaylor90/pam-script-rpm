%global upstream_name pam_script
%global selinux_variants mls strict targeted
%global selinux_policyver %(%{__sed} -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp || echo 0.0.0)

Name:           pam-script
Version:        1.1.7
Release:        0%{?dist}
Summary:        PAM module for executing scripts

Group:          Applications/System
License:        GPLv2
URL:            https://github.com/jeroennijhof/pam_script
Source0:        %{name}-%{version}.tar.gz
Source1:        %{name}.te
Source2:        %{name}.fc
Source3:        %{name}.if

BuildRequires:  pam-devel 
BuildRequires:  checkpolicy
BuildRequires:  selinux-policy-devel
BuildRequires:  selinux-policy-doc

Requires:       pam       
%if "%{selinux_policyver}" != ""
Requires:       selinux-policy >= %{selinux_policyver}
%endif
Requires:       policycoreutils
Requires:       policycoreutils-python

%description
pam_script is a module which allows to execute scripts after opening
and/or closing a session using PAM.

%prep
%setup -q 
cp etc/README etc/README.module_types

mkdir SELinux
cp -p %{SOURCE1} %{SOURCE2} %{SOURCE3} SELinux

%build
%configure --libdir=/%{_lib}/security
make %{?_smp_mflags}

cd SELinux
for selinuxvariant in %{selinux_variants}
do
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  mv %{name}.pp %{name}.pp.${selinuxvariant}
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
cd -

%install
make install DESTDIR=%{buildroot}

rm %{buildroot}%{_sysconfdir}/README

for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 SELinux/%{name}.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{name}.pp
done

%post
for selinuxvariant in %{selinux_variants}
do
  /usr/sbin/semodule -s ${selinuxvariant} -i \
    %{_datadir}/selinux/${selinuxvariant}/%{name}.pp &> /dev/null || :
done

%postun
if [ $1 -eq 0 ] ; then
  for selinuxvariant in %{selinux_variants}
  do
     /usr/sbin/semodule -s ${selinuxvariant} -r %{name} &> /dev/null || :
  done
fi

%posttrans
# apply new SELinux file context
restorecon "%{_sysconfdir}/pam_script*"
restorecon "%{_sysconfdir}/pam-script.d/*"

%files
%doc AUTHORS COPYING ChangeLog README NEWS etc/README.module_types etc/README.pam_script SELinux/*
%dir %{_sysconfdir}/pam-script.d/
%{_sysconfdir}/pam_script*
/%{_lib}/security/*
%{_mandir}/man7/%{name}.7*
%{_datadir}/selinux/*/%{name}.pp

%changelog
* Thu May 01 2014 Jason Taylor <jason.taylor@secure-24.com> 1.1.7-0
- Initial RPM build
