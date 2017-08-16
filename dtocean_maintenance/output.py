# -*- coding: utf-8 -*-
"""
@author: WavEC Offshore Renewables, Mathew Topper
email: boris.teillant@wavec.org; paulo@wavec.org, pedro.vicente@wavec.org,
       dataonlygreater@gmail.com

The function out_process processes the results to be outputed from the
logistics module
"""

def out_process(log_phase, module):

    # INITIAL:
    nr_ves_p_type = []
    nr_ves_p_type_quant = []
    nr_eq_p_type = []
    nr_eq_p_type_quant = []
    nr_vecomb_p_seq = []
    seq_descrip = []
    op_in_seq_total = {}

    for ind_seq in range(len(log_phase.op_ve_init)):

        seq_init = log_phase.op_ve_init[ind_seq]
        seq_ve = log_phase.op_ve[ind_seq]

        nr_vecomb_p_seq.append(len(seq_init.ve_combination))
        seq_descrip.append(seq_init.description)

        op_in_seq = []

        for ind_prep_op in range(len(seq_ve.op_seq_prep)):
            op_in_seq.append(seq_ve.op_seq_prep[ind_prep_op].description)

        for ind_sea_op in range(len(seq_ve.op_seq_sea)):
            for ind_smt in range(len(seq_ve.op_seq_sea[ind_sea_op])):

                seq_smt = seq_ve.op_seq_sea[ind_sea_op][ind_smt]
                op_in_seq.append(seq_smt.description)

        for ind_demob_op in range(len(seq_ve.op_seq_demob)):
            op_in_seq.append(seq_ve.op_seq_demob[ind_demob_op].description)

        op_in_seq_total.update({seq_init.description: op_in_seq})

        for ind_combi in range(len(seq_init.ve_combination)):

            seq_combi = seq_init.ve_combination[ind_combi]

            for ind_ves_type in range(len(seq_combi['vessel'])):

                new_vess = seq_combi['vessel'][ind_ves_type][1].id
                new_vess_len = len(seq_combi['vessel'][ind_ves_type][1].panda)
                vess_repeat = 0

                for ind_vess in range(len(nr_ves_p_type)):
                    if new_vess == nr_ves_p_type[ind_vess]:
                        vess_repeat = 1
                        break

                if vess_repeat == 0:
                   nr_ves_p_type.append(new_vess)
                   nr_ves_p_type_quant.append([new_vess, new_vess_len])

            for ind_eq_type in range(len(seq_combi['equipment'])):

                new_eq = seq_combi['equipment'][ind_eq_type][1].id
                new_eq_len = len(seq_combi['equipment'][ind_eq_type][1].panda)
                eqs_repeat = 0

                for ind_eq in range(len(nr_eq_p_type)):
                    if new_eq == nr_eq_p_type[ind_eq]:
                        eqs_repeat = 1
                        break

                if eqs_repeat == 0:
                   nr_eq_p_type.append(new_eq)
                   nr_eq_p_type_quant.append([new_eq, new_eq_len])

    nv_ve_combi_init = sum(nr_vecomb_p_seq)

    # FEASABILITY:
    ves_types_feas = []
    ves_types_feas_quant = []
    eqs_types_feas = []
    eqs_types_feas_quant = []

    for ind_seq in range(len(log_phase.op_ve)):

       for ind_combi in range(len(log_phase.op_ve[ind_seq].ve_combination)):

           seq_combi = log_phase.op_ve[ind_seq].ve_combination[ind_combi]

           for ind_ves_type in range(len(seq_combi['vessel'])):

               new_vess = seq_combi['vessel'][ind_ves_type][1].id
               new_vess_len = len(seq_combi['vessel'][ind_ves_type][1].panda)
               vess_repeat = 0

               for ind_vess in range(len(ves_types_feas)):
                    if new_vess == ves_types_feas[ind_vess]:
                        vess_repeat = 1
                        break

               if vess_repeat == 0:
                   ves_types_feas.append(new_vess)
                   ves_types_feas_quant.append([new_vess, new_vess_len])


           for ind_eq_type in range(len(seq_combi['equipment'])):

               new_eq = seq_combi['equipment'][ind_eq_type][1].id
               new_eq_len = len(seq_combi['equipment'][ind_eq_type][1].panda)
               eqs_repeat = 0

               for ind_eq in range(len(eqs_types_feas)):
                    if new_eq == eqs_types_feas[ind_eq]:
                        eqs_repeat = 1
                        break

               if eqs_repeat == 0:
                   eqs_types_feas.append(new_eq)
                   eqs_types_feas_quant.append([new_eq, new_eq_len])


    # MATCHING:
    ves_types = []
    eqs_types = []
    vess_all = []
    eqs_all = []

    for ind_seq in range(len(log_phase.op_ve)):

        # a strategy with no solutions!
        if len(module['combi_select'][ind_seq]) == 0:
            continue

        for ind_sol in range(len(module['combi_select'])):

            seq_sol = module['combi_select'][ind_seq][ind_sol]

            for ind_vess_type_sol in range(len(seq_sol['VEs'])):

                seq_vess_type = seq_sol['VEs'][ind_vess_type_sol]

                # vessel:
                new_vess = seq_vess_type[0]

                # check if repeted vessel
                vess_repeat = 0

                for ind_vess in range(len(ves_types)):
                    if new_vess == ves_types[ind_vess]:
                        vess_repeat = 1
                        vess_all.append([new_vess,
                                         seq_vess_type[2].name])
                        break

                if vess_repeat == 0:
                    ves_types.append(new_vess)
                    vess_all.append([new_vess,
                                     seq_vess_type[2].name])

                # equipment:
                if len(seq_vess_type) > 3:

                    nr_equip = len(seq_vess_type) - 3

                    for ind_eqs_in_vess in range(nr_equip):

                        seq_equip = seq_vess_type[3 + ind_eqs_in_vess]
                        new_equip = seq_equip[0]

                        # check if repeted vessel
                        eqs_repeat = 0

                        for ind_eqs in range(len(eqs_types)):

                            if new_equip == eqs_types[ind_eqs]:
                                eqs_repeat = 1
                                eqs_all.append([new_equip,
                                            seq_equip[2].name])
                                break

                        if eqs_repeat == 0:
                            eqs_types.append(new_equip)
                            eqs_all.append([new_equip,
                                            seq_equip[2].name])

    # SOLUTIONS:
    sol_in_seq = []
    sols_all = []

    for ind_seq in range(len(log_phase.op_ve)):

        sol_in_seq.append(len(log_phase.op_ve[ind_seq].sol))
        sols_all.append(log_phase.op_ve[ind_seq].sol)

    # VESSELS!!
    # inicializar dicionario com vessel type usados
    ves_types_match = {}

    for ind_ves_type in range(len(ves_types)):
        ves_types_match[ves_types[ind_ves_type]] = {}

    # contabilizar por index...........
    for ind_vess_all in range(len(vess_all)):

        ves_type_i = vess_all[ind_vess_all][0]
        ves_index_i = vess_all[ind_vess_all][1]

        if ves_index_i in ves_types_match[ves_type_i]:
            ves_types_match[ves_type_i][ves_index_i] += 1
        else:
            ves_types_match[ves_type_i].update({ ves_index_i: 1})

    ves_types_match_quant = []

    for ind_vess_match in range(len(ves_types)):

        ves_match = ves_types[ind_vess_match]
        ves_types_match_quant.append([ves_match,
                                      len(ves_types_match[ves_match])])

    # EQUIPMENTS!!
    # inicializar dicionario com vessel type usados
    eqs_types_match = {}

    for ind_eqs_type in range(len(eqs_types)):
        eqs_types_match[eqs_types[ind_eqs_type]] = {}

    # contabilizar por index...........
    for ind_eqs_all in range(len(eqs_all)):

        eqs_type_i = eqs_all[ind_eqs_all][0]
        eqs_index_i = eqs_all[ind_eqs_all][1]

        if eqs_index_i in eqs_types_match[eqs_type_i]:
            eqs_types_match[eqs_type_i][eqs_index_i] += 1
        else:
            eqs_types_match[eqs_type_i].update({eqs_index_i: 1})

    eqs_types_match_quant = []

    for ind_eqs_match in range(len(eqs_types)):

        eq_match = eqs_types[ind_eqs_match]
        eqs_types_match_quant.append([eq_match,
                                      len(eqs_types_match[eq_match])])


    # SOLUTION:
    VE_sol = module['optimal']['vessel_equipment']
    vess_in_sol = []
    eqs_in_sol = []

    for ind_vess_sol in range(len(VE_sol)):

       vess_in_sol.append(VE_sol[ind_vess_sol][0])

       if len(VE_sol[ind_vess_sol]) > 3:

           nr_equip = len(VE_sol[ind_vess_sol]) - 3

           for ind_eqs_in_vess in range(nr_equip):
                eqs_in_sol.append(VE_sol[ind_vess_sol][3 + ind_eqs_in_vess][0])


    OUTPUT_dict =  {
                    'logistic_phase_description': log_phase.description,

                    'ves_req': {'deck area':
                                    module['requirement'][5]['deck area'],
                                'deck cargo':
                                    module['requirement'][5]['deck cargo'],
                                'deck loading':
                                    module['requirement'][5]['deck loading'],
                                'crane capacity':
                                    module['requirement'][5]['deck cargo']},

                    'ves_types_init': nr_ves_p_type_quant,
                    'eq_types_init': nr_eq_p_type_quant,

                    'ves_req_feas': module['requirement'][1],
                    'eq_req_feas': module['requirement'][0],

                    'ves_types_feas': ves_types_feas_quant,
                    'eq_types_feas': eqs_types_feas_quant,

                    'port_ves_req': module['requirement'][2],
                    'ves_eq_req': module['requirement'][4],

                    'ves_types_match': ves_types_match_quant,
                    'eq_types_match': eqs_types_match_quant,

                    'nb_sol': sum(sol_in_seq),
                    'sol': sols_all,
                    'nb_strat': seq_descrip,
                    'nb_task': op_in_seq_total,

                    'sched_all': module['schedule'],
                    'cost_all': module['cost'],

                    'risk_all': module['risk'],
                    'env_all': module['envir'],

                    'opt_sol': {
                                'vessel_equipment':
                                    module['optimal']['vessel_equipment'],

                                'port': module['port'],

                                'total_wait_time [h]':
                                    module['optimal']['schedule waiting time'],
                                'total_sea_time [h]':
                                    module['optimal']['schedule sea time'],
                                'total_prep_time [h]':
                                    module['optimal']['schedule prep time'],
                                'total_time [h]':
                                    module['optimal'][
                                            'schedule total sea time'],

                                'nb_journeys [-]':
                                    module['optimal']['numb of journeys'],

                                'start_dt': module['optimal']['start_dt'],
                                'depart_dt': module['optimal']['depart_dt'],
                                'end_dt': module['optimal']['end_dt'],

                                'total_vessel_cost [EUR]':
                                    module['optimal']['vessel cost'],
                                'total_eq_cost [EUR]':
                                    module['optimal']['equipment cost'],
                                'total_port_cost [EUR]':
                                    module['optimal']['port cost'],
                                'total_fuel_cost [EUR]':
                                    module['optimal']['fuel cost'],
                                'total_cost [EUR]':
                                    module['optimal']['total cost']
                                }
    }

    return OUTPUT_dict
