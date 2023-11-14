import dateutil.parser
import bson
import metadataConf
import datetime

#TODO: how to we always assure that message have last u

class messageParser(dict):
    """Checked the correctnes of the message that will be inserted to mxdb
    """
    def __init__(self, *args, **kwargs):
        super(messageParser, self).__init__(*args, **kwargs)
        self.update(kwargs)

        self.merge_status_keys = [u'mergeId', u'trackingId', u'datasetCount', \
                                  u'userAccount', u'beamline', u'lastUpdated', u'method',\
                                  u'datasetList', u'datasetNumbers']

        self.current_merge_id_keys = [u'mergeId', u'trackingId', u'beamline', u'userAccount', u'lastUpdated', 'method']

        self.valid_for_remove_from_merge_state_keys = [u'beamline', u'mergeId', u'method', u'trackingId', u'userAccount']
        
        self.valid_for_restore_merge_state_keys = [u'beamline', u'counter']
        
        self.valid_for_merge_state_keys = [u'beamline', u'mergeId', u'method', u'trackingId', u'userAccount', u'datasetCount', u'datasetList', u'datasetNumbers', u'lastUpdated']

        self.excluded_from_metadata = metadataConf.excluded_from_metadata

        self.__normalize()


    def __normalize(self):
        '''Normalizes common keys to make sure they are same across the database.
           - name of the beamline will be lowercase 'x06sa'
           - parsing the values of the dates
        '''

        # Normalize beamline name
        beamline_aliases = {u'pxi': u'x06sa',   u'pxii': u'x10sa', u'pxiii': u'x06da',\
                            u'x06sa': u'x06sa', u'x10sa': u'x10sa', u'x06da': u'x06da'}

        try:
            self['beamline'] = self['beamline'].lower()
            try:
                self['beamline'] = beamline_aliases[self['beamline']]
            except KeyError as e: 
                raise Exception('Invalid beamline name: {}'.format(e))
        except KeyError:
            pass # It is not required that this key exists for all the messages
        
        try:
            self[u'createdOn'] = dateutil.parser.parse(self[u'createdOn'])
        except KeyError:
            pass 
        except ValueError:
            raise Exception('Cannot parse the date in createdOn. Wrong string format')
                    
        try:
            self[u'lastUpdated'] = dateutil.parser.parse(self[u'lastUpdated'])
        except KeyError:
            pass
        except ValueError:
            raise Exception('Cannot parse the date in lastUpdated. Wrong string format')
 
        try:
            self[u'_id'] = bson.ObjectId(self[u'_id'])
        except (KeyError, bson.errors.InvalidId):
            pass

        try:
            for status in self[u'statusHistory'].keys():
                self['statusHistory'][status]['pending'] = dateutil.parser.parse(self['statusHistory'][status]['pending'])
        except (KeyError, TypeError):
            pass

    
    def default(self):
        '''Always accepts the format of the message'''
        return True

    def valid_for_merge_status(self):
        '''Performs strict check is message is valid for MergeStatus collection'''

        return set(self) == set(self.merge_status_keys)

    def valid_for_current_mergeId(self):
        '''Performs strict check is message is valid to update current MergeId in MergeStatus collection'''
        if set(self) == set(self.current_merge_id_keys):
            if self['mergeId'] != None and self['trackingId'] != None: # both trackingId and mergeId givne
                return False
            elif self['mergeId'] == None and self['trackingId'] == None: # both mergeId and trackingId have no value
                return False
            else:
                return True # either mergeId or trackingId are given value
        else:
            return False # not all the required keys are given

    def valid_for_remove_from_merge_state(self):
        '''Performs check if message is valid update to restore_mxdb counter with values from Merge Manager'''
        return set(self) == set(self.valid_for_remove_from_merge_state_keys)

    def valid_for_restore_merge_state(self):
        '''Performs check if message is valid completetly restore MergeState collection by Merge Manager'''
        return set(self) == set(self.valid_for_restore_merge_state_keys)
    
    def valid_for_merge_state(self):
        '''Performs check if message is valid to be inserted to MergeState from Merge Manager'''
        return set(self) == set(self.valid_for_merge_state_keys)
            
    def gen_metadata(self, label = u'metadata'):
        '''
        Create metadata as list of dictionaries of the form:
        label : [{name:N1, value:V1}, {name:N2, value:V2}, ...]

        The default label is 'metadata'.
        '''

        if label in self and not isinstance(self[label],list):
            raise Exception('Cannot create metatada. Key "{}" already exists in the message and is not a list. Current value:{}'.format(label,self[label]))

        if label not in self:
            self[label] = []
        
        keys = list(self.keys())# copy as list, so one can iterate and pop keys at the same time

        for k in keys:
            if k not in self.excluded_from_metadata:
                v = self.pop(k)
                self[label].append({u'name':k, u'value':v})        

