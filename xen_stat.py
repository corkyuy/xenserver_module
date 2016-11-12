#!/usr/bin/python

DOCUMENTATION = '''
---
module: xen_stat
version_added: "1.0"
short_description: retrieve xenserver information
description:
     - Retrieves facts for a xenserver
options:
  vm:
    description:
      - Name of VM
    required: true
    default: null
author: "Corky Uy (@corkyuy)"
'''

EXAMPLES = '''
# Obtain the stats of /etc/foo.conf, and check that the file still belongs
# to 'root'. Fail otherwise.
- xen_stat: vm=Test
  register: st
- fail: msg="Whoops! file ownership has changed"
  when: st.xen_stat.status != 'Running'
'''

RETURN = '''
xen_stat:
'''

import platform
from ansible.module_utils.basic import *


HAVE_XENAPI = False
try:
    import XenAPI
    HAVE_XENAPI = True
except ImportError:
    pass

def get_xenapi_session():
    session = XenAPI.xapi_local()
    session.xenapi.login_with_password('', '')
    return session

def vm_start(session, vm):
    session.xenapi.VM.start(vm, False, True)
    return True

def vm_shutdown(session, xs_vm):
    session.xenapi.VM.shutdown(xs_vm)
    return True

def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm=dict(required=True, type='str'),
            state=dict(required=False, type='str'),
            follow=dict(default='no', type='bool'),
            get_md5=dict(default='yes', type='bool'),
            get_checksum=dict(default='yes', type='bool'),
            checksum_algorithm=dict(default='sha1', type='str',
                                    choices=['sha1', 'sha224', 'sha256', 'sha384', 'sha512'],
                                    aliases=['checksum_algo', 'checksum']),
            mime=dict(default=False, type='bool', aliases=['mime_type', 'mime-type']),
        ),
        supports_check_mode=True
    )

    if not HAVE_XENAPI:
        module.fail_json(msg="python xen api required for this module")

    try:
        session = get_xenapi_session()
    except XenAPI.Failure as e:
        module.fail_json(msg='%s' % e)

    name = module.params.get('vm')
    state = module.params.get('state')

    vm = session.xenapi.VM.get_by_name_label(name)[0]

    if not vm:
        module.fail_json(msg="virtual machine %s not found" % vm)

    curr_power_state = session.xenapi.VM.get_power_state(vm)
    change=False
    failed=False

    if state and not(state==curr_power_state):
        ret = False
        if state == 'Running':
            ret = vm_start(session, vm)
        if state == 'Halted':
            ret = vm_shutdown(session, vm)
        curr_power_state = session.xenapi.VM.get_power_state(vm)
        if not( state == curr_power_state ):
            failed=True
        if state == curr_power_state:
            change=True

    output={
        'name':name,
        'power_state':str(curr_power_state),
        }
    module.exit_json(changed=change, failed=failed, xen_stat=output)

if __name__ == '__main__':
    main()
