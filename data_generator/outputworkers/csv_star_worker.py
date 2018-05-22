import data_generator.config.out as out_cfg
import data_generator.writers.writecsv as csv_writer
from data_generator.model.assessment import Assessment
from data_generator.model.assessmentoutcome import AssessmentOutcome
from data_generator.model.institutionhierarchy import InstitutionHierarchy
from data_generator.model.interimassessmentoutcome import InterimAssessmentOutcome
from data_generator.model.student import Student
from data_generator.outputworkers.worker import Worker


class CSVStarWorker(Worker):
    def __init__(self, root_path: str):
        self.root_path = root_path

    def prepare(self):
        csv_writer.clean_dir(self.root_path)
        # Prepare star-schema output files
        csv_writer.prepare_csv_file(out_cfg.FAO_VW_FORMAT['name'], out_cfg.FAO_VW_FORMAT['columns'], self.root_path)
        csv_writer.prepare_csv_file(out_cfg.FAO_FORMAT['name'], out_cfg.FAO_FORMAT['columns'], self.root_path)
        csv_writer.prepare_csv_file(out_cfg.FBAO_FORMAT['name'], out_cfg.FBAO_FORMAT['columns'], self.root_path)
        csv_writer.prepare_csv_file(out_cfg.DIM_STUDENT_FORMAT['name'], out_cfg.DIM_STUDENT_FORMAT['columns'], self.root_path)
        csv_writer.prepare_csv_file(out_cfg.DIM_INST_HIER_FORMAT['name'], out_cfg.DIM_INST_HIER_FORMAT['columns'], self.root_path)
        csv_writer.prepare_csv_file(out_cfg.DIM_ASMT_FORMAT['name'], out_cfg.DIM_ASMT_FORMAT['columns'], self.root_path)
        csv_writer.prepare_csv_file(out_cfg.SR_FORMAT['name'], out_cfg.SR_FORMAT['columns'], self.root_path)

    def write_assessments(self, asmts: [Assessment]):
        file_name = out_cfg.DIM_ASMT_FORMAT['name']
        csv_writer.write_records_to_file(file_name, out_cfg.DIM_ASMT_FORMAT['columns'], asmts, tbl_name='dim_asmt', root_path=self.root_path)

    def write_hierarchies(self, hierarchies: [InstitutionHierarchy]):
        csv_writer.write_records_to_file(out_cfg.DIM_INST_HIER_FORMAT['name'],
                                         out_cfg.DIM_INST_HIER_FORMAT['columns'], hierarchies,
                                         tbl_name='dim_hier', root_path=self.root_path)

    def write_students_dim(self, students: [Student]):
        csv_writer.write_records_to_file(out_cfg.DIM_STUDENT_FORMAT['name'],
                                         out_cfg.DIM_STUDENT_FORMAT['columns'], students,
                                         entity_filter=('held_back', False), tbl_name='dim_student',
                                         root_path=self.root_path)

    def write_students_reg(self, students: [Student], rs_guid, asmt_year):
        csv_writer.write_records_to_file(out_cfg.STUDENT_REG_FORMAT['name'],
                                         out_cfg.STUDENT_REG_FORMAT['columns'],
                                         students, tbl_name='student_reg',
                                         root_path=self.root_path)

    def write_iab_outcome(self, results: [InterimAssessmentOutcome], guid):
        csv_writer.write_records_to_file(out_cfg.FBAO_FORMAT['name'], out_cfg.FBAO_FORMAT['columns'], results,
                                         tbl_name='fact_block_asmt_outcome', root_path=self.root_path)

    def write_assessment_outcome(self, results: [AssessmentOutcome], guid, state_code, district_id):
        csv_writer.write_records_to_file(out_cfg.FAO_VW_FORMAT['name'], out_cfg.FAO_VW_FORMAT['columns'], results,
                                         tbl_name='fact_asmt_outcome_vw', root_path=self.root_path)
        csv_writer.write_records_to_file(out_cfg.FAO_FORMAT['name'], out_cfg.FAO_FORMAT['columns'], results,
                                         tbl_name='fact_asmt_outcome', root_path=self.root_path)
