"""
Functions for deal with double-count tenures, i.e. the same person/ID in two places at the same time.
"""

import person_id_assigner
import transdict_tools
import iter_helpers


def remove_double_count_tenures(table):
    """
    returns a table where rows that double count (example below) are removed.
    Essentially this corrects base-level book-keeping hiccups, where for the transition month(s) the person
    was recorded as employed by both the place they left and the place they joined
    e.g.
    ('2015-06', ['CA4.TB12.J44'])
    ('2015-07', ['CA8.TB27.-88', 'CA4.TB12.J44'])
    ('2015-08', ['CA8.TB27.-88'])
    and this function removes 'CA4.TB12.J44' in the double counted row
    """
    ym_unit_dict = iter_helpers.make_ym_unit_dict(table)  # for each ID make a dict of years-months: units
    # get IDs with >1 unit per year-month; can't be in two places at once
    overlap_ids = person_id_assigner.get_overlap_ids(ym_unit_dict)

    rows_for_removal = set()
    for oid in overlap_ids:
        seq = sorted(ym_unit_dict[oid].items(), key=lambda x: x[0])  # make chronological year-month sequences
        for idx, elem in enumerate(seq):
            if len(elem[1]) > 1:  # sequence element with multiple locations at same time-spot
                # for each additional double-counted month, mark for removal that unit duplicating the place
                # we just left, unless at beginning of sequence, then remove duplicate of destination
                last_month_unit = seq[idx - 1][1] if idx > 1 else ''
                units_ahead = units_months_ahead(seq, idx, 5)

                # one month ahead
                if len(last_month_unit) <= 1 and len(units_ahead[0]) <= 1:
                    removal_unit = last_month_unit[0] if last_month_unit != '' else units_ahead[0][0]
                    add_removal_rows(rows_for_removal, seq, idx, oid, 1, removal_unit)
                    month_jump_typo_catcher(elem, last_month_unit, units_ahead[0], rows_for_removal, oid)

                # two months ahead
                elif len(last_month_unit) <= 1 and len(units_ahead[1]) <= 1 < len(units_ahead[0]):
                    removal_unit = last_month_unit[0] if last_month_unit != '' else units_ahead[1][0]
                    add_removal_rows(rows_for_removal, seq, idx, oid, 2, removal_unit)

                # three months ahead
                elif len(last_month_unit) <= 1 and len(units_ahead[2]) <= 1 < len(units_ahead[0]):
                    removal_unit = last_month_unit[0] if last_month_unit != '' else units_ahead[2][0]
                    add_removal_rows(rows_for_removal, seq, idx, oid, 3, removal_unit)

                # four months ahead
                elif len(last_month_unit) <= 1 and len(units_ahead[3]) <= 1 < len(units_ahead[0]):
                    removal_unit = last_month_unit[0] if last_month_unit != '' else units_ahead[3][0]
                    add_removal_rows(rows_for_removal, seq, idx, oid, 4, removal_unit)

                # five months ahead
                elif len(last_month_unit) <= 1 and len(units_ahead[4]) <= 1 < len(units_ahead[0]):
                    removal_unit = last_month_unit[0] if last_month_unit != '' else units_ahead[4][0]
                    add_removal_rows(rows_for_removal, seq, idx, oid, 5, removal_unit)

    new_table = []
    for row in table:
        identifiers = (row[0], row[5] + '-' + row[6], '.'.join(row[-3:]))
        if identifiers in rows_for_removal:
            continue
        else:
            new_table.append(row)
    return new_table


def month_jump_typo_catcher(sequence_element, last_months_unit, next_months_unit, removal_set, oid):
    """
    assume below is a typo: hard to believe someone jumped courts for just one month
    # ('2009-04', ['CA8.TB28.J103'])
    # ('2010-05', ['CA8.TB28.-88', 'CA6.TB20.-88'])
    # ('2010-06', ['CA8.TB28.-88'])
    """
    for unit in sequence_element[1]:
        if last_months_unit != '' and next_months_unit != '':
            if (unit != last_months_unit[0]) and (unit != next_months_unit[0]):
                removal_set.add((oid, sequence_element[0], unit))


def units_months_ahead(sequence, idx, months_ahead):
    """return the units associated with X many months ahead"""
    months_ahead_units = []
    for ma in range(1, months_ahead + 1):
        months_ahead_units.append(sequence[idx + ma][1] if idx < len(sequence) - ma else '')
    return months_ahead_units


def add_removal_rows(removal_set, sequence, idx, oid, month_ahead, removal_unit):
    """for each month ahead adds a tuple with row identifiers to the row removal set"""
    for ma in range(month_ahead):
        removal_set.add((oid, sequence[idx + ma][0], removal_unit))


def split_coinciding_sequences(table):
    """
    some IDs are in two places at the same time -- impossible;
    split apart coinciding career sequences and give them new IDs
    return an updated table
    """
    # for each ID make a dict of years-months: units
    ym_unit_dict = iter_helpers.make_ym_unit_dict(table)
    # get IDs with >1 unit per year-month; can't be in two places at once
    overlap_ids = person_id_assigner.get_overlap_ids(ym_unit_dict)
    seqs_to_be_relabelled = []
    for oid in overlap_ids:
        seq = sorted(ym_unit_dict[oid].items(), key=lambda x: x[0])  # make chronological year-month sequences
        overlap_ids = []
        for idx, elem in enumerate(seq):
            if len(elem[1]) > 1:
                overlap_ids.append(idx)

        unit_before_overlap = seq[overlap_ids[0] - 1][1][0] if overlap_ids[0] != 0 else 'overlaps from beginning'
        unit_after_overlap = seq[overlap_ids[-1] + 1][1][0] if overlap_ids[-1] != len(seq) - 1 else 'overlaps to end'

        new_sequence = []
        for idx, elem in enumerate(seq):
            if len(elem[1]) > 1:
                for unit in elem[1]:
                    if unit_before_overlap == 'overlaps from beginning' and unit_after_overlap == 'overlaps to end':
                        new_sequence = bin_units_by_appellate(oid, seq)
                    elif unit_before_overlap == 'overlaps from beginning' and unit_after_overlap != 'overlaps to end':
                        # make separate sequence of units in different CA's
                        if unit.split('.')[0] == unit_after_overlap.split('.')[0]:
                            new_sequence.append((oid, elem[0], unit))
                    elif unit_before_overlap != 'overlaps from beginning' and unit_after_overlap == 'overlaps to end':
                        if unit.split('.')[0] == unit_before_overlap.split('.')[0]:
                            new_sequence.append((oid, elem[0], unit))
                    else:
                        if unit.split('.')[0] == unit_before_overlap.split('.')[0]:
                            new_sequence.append((oid, elem[0], unit))
        if new_sequence:
            if isinstance(new_sequence, dict):
                for i in new_sequence.values():
                    seqs_to_be_relabelled.append(i)
            else:
                seqs_to_be_relabelled.append(new_sequence)

                # TODO need to catch the seqs that still are overlapped -- maybe check for overlaps in
                # if condition and if overlaps recurse?

    # finally, relabel the rows of these sequences in the table with a new ID
    max_id = max(iter_helpers.collect_of_row_results(table, "list", lambda x: int(x[0])))
    new_ids = [int(max_id) + i for i in range(1, len(seqs_to_be_relabelled) + 1)]

    for idx, s in enumerate(sorted(seqs_to_be_relabelled)):
        id_num = new_ids[idx]
        for index, row in enumerate(table):
            identifiers = (row[0], row[5] + '-' + row[6], '.'.join(row[-3:]))
            if identifiers in set(s):
                table[index][0] = str(id_num)
    return table


def bin_units_by_appellate(id_num, sequence_as_list):
    """return a dict of sequences, each corresponding to a sequence in a different appellate branch"""
    bins = {ca: [] for ca in get_appellate_set(sequence_as_list)}
    for elem in sequence_as_list:
        for unit in elem[1]:
            bins[unit.split('.')[0]].append((id_num, elem[0], unit))
    return bins


def get_appellate_set(sequence_as_list):
    """return the set of appellate courts of units in the sequence"""
    appellate_set = set()
    for elem in sequence_as_list:
        for unit in elem[1]:
            appellate_set.add(unit.split('.')[0])
    return appellate_set
