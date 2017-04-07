from xml.etree.ElementTree import Element, SubElement, tostring

import os

from data_generator.model.assessmentoutcome import AssessmentOutcome
from data_generator.outputworkers.worker import Worker


class XmlWorker(Worker):
    def __init__(self, out_path_root):
        self.out_path_root = out_path_root

    def prepare(self):
        pass

    def cleanup(self):
        pass

    def write_iab_outcome(self, results: [AssessmentOutcome], assessment_guid):
        for result in results:
            self.write_asmt_to_file(result)

    def write_assessment_outcome(self, results: [AssessmentOutcome], assessment_guid, state_code, district_id):
        for result in results:
            self.write_asmt_to_file(result)

    def write_asmt_to_file(self, outcome: AssessmentOutcome):
        root = Element('TDSReport')

        # write Test
        asmt = outcome.assessment
        test = SubElement(root, 'Test')
        test.set('testId', asmt.id)
        test.set('name', asmt.name)
        test.set('bankKey', asmt.bank_key)
        test.set('subject', asmt.subject)
        test.set('grade', '{:02}'.format(asmt.grade))
        test.set('assessmentType', self.map_asmt_type(asmt.type))
        test.set('academicYear', str(asmt.year))
        test.set('assessmentVersion', asmt.version)
        test.set('contract', asmt.contract)
        test.set('mode', asmt.mode)

        # write Examinee
        student = outcome.student
        examinee = SubElement(root, 'Examinee')
        examinee.set('key', str(student.rec_id))

        # TODO - work out SSID and AlternateSSID
        contextDateStr = outcome.status_date.isoformat()
        self.add_examinee_attribute(examinee, 'StudentIdentifier', student.external_ssid, contextDateStr)
        self.add_examinee_attribute(examinee, 'Birthdate', student.dob, contextDateStr)
        self.add_examinee_attribute(examinee, 'FirstName', student.first_name, contextDateStr)
        self.add_examinee_attribute(examinee, 'MiddleName', student.middle_name, contextDateStr)
        self.add_examinee_attribute(examinee, 'LastOrSurname', student.last_name, contextDateStr)
        self.add_examinee_attribute(examinee, 'Sex', self.map_gender(student.gender), contextDateStr)
        self.add_examinee_attribute(examinee, 'GradeLevelWhenAssessed', '{:02}'.format(student.grade), contextDateStr)
        self.add_examinee_attribute(examinee, 'HispanicOrLatinoEthnicity', self.map_yes_no(student.eth_hispanic), contextDateStr)
        self.add_examinee_attribute(examinee, 'AmericanIndianOrAlaskaNative', self.map_yes_no(student.eth_amer_ind), contextDateStr)
        self.add_examinee_attribute(examinee, 'Asian', self.map_yes_no(student.eth_asian), contextDateStr)
        self.add_examinee_attribute(examinee, 'BlackOrAfricanAmerican', self.map_yes_no(student.eth_black), contextDateStr)
        self.add_examinee_attribute(examinee, 'White', self.map_yes_no(student.eth_white), contextDateStr)
        self.add_examinee_attribute(examinee, 'NativeHawaiianOrOtherPacificIslander', self.map_yes_no(student.eth_pacific), contextDateStr)
        self.add_examinee_attribute(examinee, 'DemographicRaceTwoOrMoreRaces', self.map_yes_no(student.eth_multi), contextDateStr)
        self.add_examinee_attribute(examinee, 'IDEAIndicator', self.map_yes_no(student.prg_iep), contextDateStr)
        self.add_examinee_attribute(examinee, 'LEPStatus', self.map_yes_no(student.prg_lep), contextDateStr)
        self.add_examinee_attribute(examinee, 'Section504Status', self.map_yes_no(student.prg_sec504), contextDateStr)
        self.add_examinee_attribute(examinee, 'EconomicDisadvantageStatus', self.map_yes_no(student.prg_econ_disad), contextDateStr)
        self.add_examinee_attribute(examinee, 'LanguageCode', student.lang_code, contextDateStr)
        self.add_examinee_attribute(examinee, 'EnglishLanguageProficiencyLevel', student.lang_prof_level, contextDateStr)
        # TODO - there are a few more of these

        hierarchy = outcome.inst_hierarchy
        self.add_examinee_relationship(examinee, 'StateAbbreviation', hierarchy.state.code, contextDateStr)
        self.add_examinee_relationship(examinee, 'StateName', hierarchy.state.name, contextDateStr)
        self.add_examinee_relationship(examinee, 'DistrictId', hierarchy.district.guid, contextDateStr)
        self.add_examinee_relationship(examinee, 'DistrictName', hierarchy.district.name, contextDateStr)
        self.add_examinee_relationship(examinee, 'SchoolId', hierarchy.school.guid, contextDateStr)
        self.add_examinee_relationship(examinee, 'SchoolName', hierarchy.school.name, contextDateStr)

        # write Opportunity
        opportunity = SubElement(root, 'Opportunity')
        opportunity.set('server', outcome.server)
        opportunity.set('database', outcome.database)
        opportunity.set('clientName', outcome.client_name)
        opportunity.set('status', outcome.status)
        opportunity.set('completeness', outcome.completeness)
        opportunity.set('key', outcome.guid)
        opportunity.set('oppId', str(outcome.rec_id))
        opportunity.set('opportunity', '5')         # TODO
        opportunity.set('startDate', outcome.start_date.isoformat())
        opportunity.set('statusDate', outcome.status_date.isoformat())
        opportunity.set('dateCompleted', outcome.submit_date.isoformat())
        opportunity.set('itemCount', str(len(outcome.item_data)))
        opportunity.set('ftCount', '0')
        opportunity.set('pauseCount', '0')
        opportunity.set('abnormalStarts', '0')
        opportunity.set('gracePeriodRestarts', '0')
        # opportunity.set('taId', None)
        # opportunity.set('taName', None)
        # opportunity.set('sessionId', None)
        opportunity.set('windowId', 'WINDOW_ID')    # TODO
        # opportunity.set('windowOpportunity', None)
        opportunity.set('administrationCondition', 'Valid')
        opportunity.set('assessmentParticipantSessionPlatformUserAgent', '')
        opportunity.set('effectiveDate', asmt.effective_date.isoformat())

        if outcome.assessment.segment:
            segment = SubElement(opportunity, 'Segment')
            segment.set('id', outcome.assessment.segment.id)
            segment.set('position', str(outcome.assessment.segment.position))
            segment.set('algorithm', outcome.assessment.segment.algorithm)
            segment.set('algorithmVersion', outcome.assessment.segment.algorithm_version)

        # TODO - Accommodations

        # TODO - Score

        for item_data in outcome.item_data:
            item = SubElement(opportunity, 'Item')
            item.set('bankKey', item_data.item.bank_key)
            item.set('key', item_data.item.item_key)
            item.set('position', str(item_data.item.position))
            item.set('segmentId', item_data.item.segment_id)
            item.set('format', item_data.item.type)
            item.set('operational', item_data.item.operational)
            item.set('isSelected', item_data.is_selected)
            item.set('adminDate', item_data.admin_date.isoformat())
            item.set('numberVisits', str(item_data.number_visits))
            item.set('pageNumber', str(item_data.page_number))
            item.set('pageVisits', str(item_data.page_visits))
            item.set('pageTime', str(item_data.page_time))
            item.set('responseDuration', str(item_data.page_time / 1000.0))
            item.set('dropped', item_data.dropped)
            item.set('score', str(item_data.score))
            item.set('scoreStatus', item_data.score_status)
            item.set('mimeType', 'text/plain')      # TODO
            response = SubElement(item, 'Response')
            response.set('date', item_data.response_date.isoformat())
            response.set('type', 'value')
            response.text = item_data.response_value

        xml = tostring(root, 'unicode')
        with open(self.file_path_for_outcome(outcome), "w") as f:
            f.write(xml)

    def file_path_for_outcome(self, outcome: AssessmentOutcome):
        """
        Build file path for this outcome from state, district, school, and outcome guid 
        Make sure parent folders exist.
        
        :param outcome: 
        :return: 
        """
        path = os.path.join(self.out_path_root,
                            outcome.inst_hierarchy.state.code,
                            outcome.inst_hierarchy.district.guid,
                            outcome.inst_hierarchy.school.guid)
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, outcome.guid) + '.xml'


    def add_examinee_attribute(self, parent, name, value, contextDateStr):
        if value:
            attr = SubElement(parent, 'ExamineeAttribute')
            attr.set('context', 'FINAL')
            attr.set('name', name)
            attr.set('value', str(value))
            attr.set('contextDate', contextDateStr)

    def add_examinee_relationship(self, parent, name, value, contextDateStr):
        if value:
            attr = SubElement(parent, 'ExamineeRelationship')
            attr.set('context', 'FINAL')
            attr.set('name', name)
            attr.set('value', str(value))
            attr.set('contextDate', contextDateStr)

    def map_asmt_type(self, value):
        if 'summative' in value.lower(): return 'SUM'
        if 'block' in value.lower(): return 'IAB'
        return 'ICA'

    def map_gender(self, value):
        if 'female' == value.lower(): return 'Female'
        if 'male' == value.lower(): return 'Male'
        return None

    def map_yes_no(self, value):
        return 'Yes' if value else 'No'