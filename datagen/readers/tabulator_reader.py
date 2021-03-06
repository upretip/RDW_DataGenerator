"""
A reader for the output of the assessment package tabulator.

It will produce assessment packages optionally with items.

"""

import csv
import datetime
import glob

from datagen.config import cfg
from datagen.model.assessment import Assessment
from datagen.model.item import AssessmentItem
from datagen.model.scorable import Scorable
from datagen.model.segment import AssessmentSegment
from datagen.model.subject import Subject
from datagen.util.id_gen import IDGen


def load_assessments(glob_pattern, subjects: [Subject], load_sum, load_ica, load_iab, load_items) -> [Assessment]:
    """
    Load assessments from any csv file in the given directory

    :param glob_pattern: file pattern to match and load
    :param subjects: subject definitions, correlated to assessments by subject code
    :param load_sum: True to load summative assessments
    :param load_ica: True to load ICAs
    :param load_iab: True to load IABs
    :param load_items: True to load items, False to ignore item data
    :return: loaded assessments
    """
    assessments = []
    for file in (glob.glob(glob_pattern)):
        assessments.extend(load_assessments_file(file, subjects, load_sum, load_ica, load_iab, load_items))
    return assessments


def load_assessments_file(file, subjects: [Subject], load_sum, load_ica, load_iab, load_items) -> [Assessment]:
    """
    Load assessments from a single tabulator csv file

    :param file: path of file to read
    :param subjects: subject definitions, correlated to assessments by subject code
    :param load_sum: True to load summative assessments
    :param load_ica: True to load ICAs
    :param load_iab: True to load IABs
    :param load_items: True to load items, False to ignore item data
    :return: loaded assessments
    """
    assessments = []

    def should_process(subtype):
        return ((subtype == 'SUM' or subtype == 'summative') and load_sum) \
               or (subtype == 'ICA' and load_ica) or (subtype == 'IAB' and load_iab)

    asmt = None
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        # get out early if this doesn't look like an assessments file
        if 'AssessmentId' not in reader.fieldnames:
            return assessments

        # adjust item parsing if file appears to not have item information
        parse_item = load_items and 'ItemId' in reader.fieldnames

        for row in reader:
            parse_asmt = False
            id = row['AssessmentId']

            if not asmt or asmt.id != id:
                # only load requested assessment types
                subtype = row['AssessmentSubtype']
                if not should_process(subtype):
                    print('Skipping assessment {} because type {} is not being loaded'.format(id, subtype))
                    continue

                # don't load assessments for unknown subjects
                subject_code = __mapSubject(row['AssessmentSubject'])
                subject = next((subject for subject in subjects if subject.code.upper() == subject_code.upper()), None)
                if not subject:
                    print('Skipping assessment {} for unknown subject {}'.format(id, subject_code))
                    continue

                asmt = Assessment()
                asmt.subject = subject
                assessments.append(asmt)
                parse_asmt = True

            __load_row(row, asmt, parse_asmt, parse_item)

    return assessments


def __load_row(row, asmt: Assessment, parse_asmt, parse_item):
    if parse_asmt:
        asmt.id = row['AssessmentId']
        asmt.name = row['AssessmentName']
        asmt.grade = __mapGrade(row['AssessmentGrade'])
        asmt.type = __mapAssessmentType(row['AssessmentType'], row['AssessmentSubtype'])
        asmt.version = row['AssessmentVersion']
        asmt.year = int(row['AcademicYear'])

        asmt.effective_date = datetime.date(asmt.year - 1, 8, 15)
        asmt.from_date = asmt.effective_date
        asmt.to_date = cfg.ASMT_TO_DATE

        asmt.overall = __getScorable(row, 'Scaled', 'Overall', 'Overall')

        # there may be up to 6 alt scores for an assessment
        if asmt.subject.alts:
            asmt.alts = [__getScorable(row, 'Alt' + str(i), alt_def.code, alt_def.name, alt_def.weight)
                         for (i, alt_def) in enumerate(asmt.subject.alts, start=1)]

        # claims
        if asmt.is_iab() or not asmt.subject.claims:
            asmt.claims = []
        else:
            asmt.claims = [__copyScorable(claim_def, asmt.overall.score_min, asmt.overall.score_max)
                           for claim_def in asmt.subject.claims]

        # if items are being parsed, create segment and list
        if parse_item:
            asmt.segment = AssessmentSegment()
            asmt.segment.id = IDGen.get_uuid()
            asmt.item_bank = []
            asmt.item_total_score = 0

    # infer allowed accommodations even if not parsing items
    if 'ASL' in row and len(row['ASL']) > 0:
        asmt.accommodations.add('AmericanSignLanguage')
    if 'Braille' in row and len(row['Braille']) > 0:
        asmt.accommodations.add('Braille')
    if 'AllowCalculator' in row and len(row['AllowCalculator']) > 0:
        asmt.accommodations.add('Calculator')
    if 'Spanish' in row and len(row['Spanish']) > 0:
        asmt.accommodations.add('Spanish')

    if parse_item:
        item = AssessmentItem()
        item.bank_key = row['BankKey']
        item.item_key = row['ItemId']
        item.type = row['ItemType']
        item.position = __getInt(row['ItemPosition'], 0)
        item.segment_id = asmt.segment.id
        item.max_score = int(row['MaxPoints'])
        item.dok = int(row['DOK'])
        item.difficulty = float(row['avg_b'])
        item.operational = '0' if row['IsFieldTest'] == 'true' else '1'
        item.answer_key = row['AnswerKey'] if 'AnswerKey' in row else None
        item.options_count = int(row['NumberOfAnswerOptions']) if 'NumberOfAnswerOptions' in row else 0
        # these are messy in tabulator output so split, strip, rejoin
        item.target = '|'.join(t.strip() for t in row['ClaimContentTarget'].split('|')) if 'ClaimContentTarget' in row else None
        asmt.item_bank.append(item)
        asmt.item_total_score += item.max_score


def __mapAssessmentType(type, subtype):
    if subtype == 'IAB':
        return 'IAB'
    if subtype == 'ICA':
        return 'ICA'
    if subtype == 'SUM' or subtype == 'summative':
        return 'SUM'
    raise Exception('Unexpected assessment type {}-{}'.format(type, subtype))


def __mapSubject(subject_code):
    if subject_code.lower() == 'math':
        return 'Math'
    if subject_code.lower() == 'ela':
        return 'ELA'
    return subject_code


def __mapGrade(grade):
    # we're going to be sneaky and make KG grade 0
    if grade.lower() == 'kg':
        return 0
    return int(grade)


def __getScorable(row, prefix, code, name, weight=None):
    if prefix + 'Low1' not in row:
        return None

    scorable = Scorable(code, name)
    scorable.score_min = __getScore(row[prefix + 'Low1'])
    scorable.cut_points = [s for s in [
        __getRowScore(row, prefix + 'High1'),
        __getRowScore(row, prefix + 'High2'),
        __getRowScore(row, prefix + 'High3'),
        __getRowScore(row, prefix + 'High4'),
        __getRowScore(row, prefix + 'High5')
    ] if s is not None]
    scorable.score_max = max(scorable.cut_points)
    scorable.weight = weight
    return scorable


def __copyScorable(source: Scorable, score_min, score_max):
    scorable = Scorable(source.code, source.name, score_min, score_max)
    scorable.weight = source.weight
    return scorable


def __getScore(value, default_value=None):
    try:
        return int(float(value))
    except ValueError:
        return default_value


def __getRowScore(row, label):
    return __getScore(row[label]) if label in row else None


def __getInt(value, default_value):
    try:
        return int(value)
    except ValueError:
        return default_value
