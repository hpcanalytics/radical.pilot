
__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__   = "MIT"

from .panda_nge import PandaNGE

from .session                   import *
from .pilot_manager             import *
from .unit_manager              import *
from .compute_unit_description  import *
from .compute_pilot_description import *
from .states                    import *

RP   = 'radical.pilot'
RPS  = 'radical.pilot.service'
DB   = 'radical.pilot.db'

# --------------------------------------------------------------------------
#
# see https://docs.google.com/document/d/1bm8ucgfi9SHjDy0w-ZX5NIdkjk87qFClMB9jMse75uM
#
class PandaNGE_RP(PandaNGE):
    '''
    This is the RP bound implementation of the abstract PandaNGE class/
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, url=None):
        '''
        url: contact point (unused)
        '''

        self._url = url
        self._session = Session()
        self._pmgr    = PilotManager(self._session)
        self._umgr    = UnitManager(self._session)


        try:
            pilot_descriptions = ru.read_json('./panda_nge_pilot.json')
        except:
            pilot_descriptions = [{'resource': 'local.localhost', 
                                   'cores'   : 4, 
                                   'runtime' : 15}]

        pds = list()
        for pd in pilot_descriptions:
            pds.append(ComputePilotDescription(pd))

        pilots = self._pmgr.submit_pilots(pds)
        self._umgr.add_pilots(pilots)


    # --------------------------------------------------------------------------
    #
    @property
    def uid(self):

        return self._session.uid


    # --------------------------------------------------------------------------
    #
    def close(self):

        self._session.close()


    # --------------------------------------------------------------------------
    #
    def list_resources(self):

        return [pilot.uid for pilot in self._pmgr.get_pilots()]


    # --------------------------------------------------------------------------
    #
    def find_resources(self, states=None):

        if   not states                  : states = list()
        elif not isinstance(states, list): states = [states]

        ret = list()
        if states:
            for pilot in self._pmgr.get_pilots():
                if pilot.state in states:
                    ret.append(pilot.uid)
        else:
            ret = self._pmgr.list_pilots()

        return ret


    # --------------------------------------------------------------------------
    #
    def get_resource_info(self, resource_ids=None):

        if   not resource_ids                  : resource_ids = list()
        elif not isinstance(resource_ids, list): resource_ids = [resource_ids]

        ret = list()
        if resource_ids:

            pilots = self._pmgr.get_pilots()

            if   not pilots                  : pilots = list()
            elif not isinstance(pilots, list): pilots = [pilots]

            for pilot in pilots:
                if pilot.uid in resource_ids:
                    ret.append(pilot.as_dict())
        else:
            for pilot in self._pmgr.get_pilots():
                ret.append(pilot.as_dict())

        return ret


    # --------------------------------------------------------------------------
    #
    def get_resource_states(self, resource_ids=None):

        pilots = self._pmgr.get_pilots(resource_ids)

        if   not pilots                  : pilots = list()
        elif not isinstance(pilots, list): pilots = [pilots]

        return [pilot.state for pilot in pilots]


    # --------------------------------------------------------------------------
    #
    def wait_resource_states(self, resource_ids=None, states=None, timeout=None):

        return self._pmgr.wait_pilots(uids=resource_ids, state=states,
                                      timeout=timeout)


    # --------------------------------------------------------------------------
    #
    def submit_tasks(self, descriptions):

        cuds = list()
        for descr in descriptions:
            cuds.append(ComputeUnitDescription(descr))

        units = self._umgr.submit_units(cuds)

        return [unit.uid for unit in units]


    # --------------------------------------------------------------------------
    #
    def list_tasks(self):

        return self._umgr.list_units()


    # --------------------------------------------------------------------------
    #
    def get_task_states(self, task_ids=None):

        if   not task_ids                  : task_ids = []
        elif not isinstance(task_ids, list): task_ids = [task_ids]

        units = self._umgr.get_units(task_ids)

        if   not units:                   units = list()
        elif not isinstance(units, list): units = [units]

        return [unit.state for unit in units]


    # --------------------------------------------------------------------------
    #
    def wait_task_states(self, task_ids=None, states=None, timeout=None):

        return self._umgr.wait_units(uids=task_ids, state=states,
                                     timeout=timeout)


# ------------------------------------------------------------------------------

