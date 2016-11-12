#!/usr/bin/python

DOCUMENTATION = '''
---
module: xen_control
version_added: "1.0"
short_description: control a xenserver 7.0
description:
     - Control a xenserver 7.0
options:
  vm:
    description:
      - Name of the virtual machine
    required: true
    default: null
  power_state:
    description:
      - Power states: Running, Halted, [Paused, Suspended]
author: "Corky Uy (@corkyuy)"
'''

EXAMPLES = '''
# Check if the virtual machine is running
- xen_control: vm=Test
  register: st
- fail: msg="Whoops! file ownership has changed"
  when: st.xen_control.power_status != 'Running'
'''

RETURN = '''
xen_control:
  power_status
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
            power_state=dict(required=False, type='str'),
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
    state = module.params.get('power_state')

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
    module.exit_json(changed=change, failed=failed, xen_control=output)

if __name__ == '__main__':
    main()
