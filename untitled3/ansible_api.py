#!/usr/bin/env python

import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    #    def v2_runner_on_ok(self, result, **kwargs):
    #        """Print a json representation of the result
    #
    #        This method could store the result in an instance attribute for retrieval later
    #        """
    #        host = result._host
    #        self.output[host] = json.dumps({host.name: result._result}, indent=4)
    #        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result


def ansibleRun(host, module, args):
    Options = namedtuple('Options',
                         ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check',
                          'diff'])
    # initialize needed objects
    loader = DataLoader()
    options = Options(connection='ssh', module_path='/path/to/mymodules', forks=100, become=None, become_method=None,
                      become_user=None, check=False,
                      diff=False)
    passwords = dict(vault_pass='secret')

    # Instantiate our ResultCallback for handling results as they come in
    results_callback = ResultCallback()

    # create inventory and pass to var manager
    # inventory = InventoryManager(loader=loader, sources=['localhost'])
    inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # create play with tasks
    play_source = dict(
        name="Ansible Play",
        hosts=host,
        gather_facts='no',
        tasks=[
            dict(action=dict(module=module, args=args), register='shell_out'),
        ]
    )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
        )
        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()

    results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
    for host, result in results_callback.host_ok.items():
        results_raw['success'][host] = result._result

    for host, result in results_callback.host_failed.items():
        results_raw['failed'][host] = result._result['msg']

    for host, result in results_callback.host_unreachable.items():
        results_raw['unreachable'][host] = result._result['msg']
    print(results_raw)
    return results_raw


if __name__ == '__main__':
    host = 'loop'
    ansibleRun(host, module='command', args='pwd')