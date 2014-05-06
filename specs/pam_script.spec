%global commit 1bb6718fa767107e97893c5fe538420ef249b0a0
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global _hardened_build 1
%global upstream_name pam_script
%global selinux_variants mls strict targeted
%global selinux_policyver %(%{__sed} -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp || echo 0.0.0)

Name:           pam_script
Version:        1.1.7
Release:        1%{?dist}
Summary:        PAM module for executing scripts

Group:          Applications/System
License:        GPLv2
URL:            https://github.com/jeroennijhof/pam_script
Source0:        https://github.com/jeroennijhof/pam_script/archive/%{commit}/pam_script-%{commit}.tar.gz
Source1:        %{name}.te
Source2:        %{name}.fc
Source3:        %{name}.if

%{?el5:BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)}

BuildRequires:  pam-devel 
BuildRequires:  checkpolicy
BuildRequires:  selinux-policy-devel
%if 0%{?rhel} > 5 || 0%{?fedora}
BuildRequires:  policycoreutils-python
%endif

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
%{?el5:rm -rf %{buildroot}}
make install DESTDIR=%{buildroot}

rm %{buildroot}%{_sysconfdir}/README

for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 SELinux/%{name}.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{name}.pp
done

%{?el5:%clean}
%{?el5:rm -rf %{buildroot}}

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
restorecon %{_sysconfdir}/pam_script*
restorecon %{_sysconfdir}/pam-script.d/

%files
%doc AUTHORS COPYING ChangeLog README NEWS etc/README.module_types etc/README.pam_script SELinux/*
%dir %{_sysconfdir}/pam-script.d/
%{_sysconfdir}/pam_script*
/%{_lib}/security/*
%{_mandir}/man7/%{name}.7*
%{_datadir}/selinux/*/%{name}.pp

%changelog
* Tue May 06 2014 Jason Taylor <jason.taylor@secure-24.com> 1.1.7-1
- Initial RPM build
