from copy import *

from sage.crypto.sbox import SBox
from claasp.cipher_modules.component_analysis_tests import binary_matrix_of_linear_component, \
    get_inverse_matrix_in_integer_representation
from claasp.cipher_modules.graph_generator import create_networkx_graph_from_input_ids
from claasp.component import Component
from claasp.components import modsub_component, cipher_output_component, linear_layer_component, \
    intermediate_output_component
from claasp.input import Input
from sage.rings.finite_rings.finite_field_constructor import FiniteField as GF
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from claasp.cipher_modules.component_analysis_tests import int_to_poly
from claasp.name_mappings import *


def get_cipher_components(self):
    # 增加代表输入的key或者plaintext的组件
    component_list = self.get_all_components()
    # print(component_list)
    for c in component_list:
        # print(c.id)
        if c.id == 'key' or c.id == 'plaintext':
            setattr(c, 'round', -1)
        else:
            setattr(c, 'round', int(c.id.split("_")[-2]))
    # build input components
    for index, input_id in enumerate(self.inputs):
        if 'key' not in self.get_all_components_ids():
            if INPUT_KEY in input_id:
                input_component = Component(input_id, "cipher_input", Input(0, [[]], [[]]), self.inputs_bit_size[index],
                                            [INPUT_KEY])
            else:
                input_component = Component(input_id, "cipher_input", Input(0, [[]], [[]]), self.inputs_bit_size[index], [input_id])
            setattr(input_component, 'round', -1)
            component_list.append(input_component)
    return component_list

def get_all_components_with_the_same_input_id_link_and_input_bit_positions(input_id_link, input_bit_positions, self):
    cipher_components = get_cipher_components(self)
    output_list = []
    for c in cipher_components:
        for i in range(len(c.input_id_links)):
            copy_input_bit_positions = copy(input_bit_positions)
            copy_input_bit_positions.sort()
            list_to_be_compared = copy(c.input_bit_positions[i])
            list_to_be_compared.sort()
            # if input_id_link == c.input_id_links[i] and list_to_be_compared in copy_input_bit_positions: #changed adding sort
            if input_id_link == c.input_id_links[i] and all(ele in copy_input_bit_positions for ele in list_to_be_compared): #changed adding sort
                output_list.append(c)
                break
    return output_list


def are_equal_components(component1, component2):
    attributes = ["id", "type", "input_id_links", "input_bit_size", "input_bit_positions", "output_bit_position", "description", "round"]
    for attr in attributes:
        if getattr(component1, attr) != getattr(component2, attr):
            return False
    return True


def add_new_component_to_list(component, component_list):  #将列表里面没有的组件加入列表
    is_in_list = False
    for c in component_list:
        if are_equal_components(component, c):
            is_in_list = True
    if not is_in_list:
        component_list.append(component)
    return


def get_output_components(component, self):  #得到以component为输入的组件列表,即component的输出组件列表
    cipher_components = get_cipher_components(self)
    output_components = []
    for c in cipher_components:
        if component.id in c.input_id_links:
            add_new_component_to_list(c, output_components)
            # output_components.append(c)
    return output_components


def is_bit_contained_in(bit, available_bits):
    for b in available_bits:
        if bit["component_id"] == b["component_id"] and \
                bit["position"] == b["position"] and \
                bit["type"] == b["type"]:
            return True
    return False

def add_bit_to_bit_list(bit, bit_list):
    if not is_bit_contained_in(bit, bit_list):
        bit_list.append(bit)
    return


def _are_all_bits_available(id, input_bit_positions_len, offset, available_bits):
    for j in range(input_bit_positions_len):
        bit = {
            "component_id": id,
            "position": offset + j,    #某个组件component的输入的位置,用offset来与输出的bit_positions相对应
            "type": "input"
        }
        if not is_bit_contained_in(bit, available_bits):
            return False
    return True

def get_available_output_components(component, available_bits, self, return_index=False):  #返回所有bit都可用的output_component
    cipher_components = get_cipher_components(self)     #return_index表示是否要返回可用输出组件的具体输入信息
    available_output_components = []
    for c in cipher_components:
        accumulator = 0
        for i in range(len(c.input_id_links)):
            if (component.id == c.input_id_links[i]) and (c not in available_output_components):
                # if component.id =='key': print(c.id)
                all_bits_available = _are_all_bits_available(c.id, len(c.input_bit_positions[i]), accumulator,
                                                             available_bits)  #组件c中component的输入位是否都是available的
                # if component.id =='key': print(all_bits_available)
                if all_bits_available:
                    if return_index:
                        available_output_components.append((c, list(range(accumulator, accumulator + len(c.input_bit_positions[i])))))
                    else:
                        available_output_components.append(c)
            accumulator += len(c.input_bit_positions[i]) # changed
    # if component.id == 'key': print('KEY_available_components:',available_output_components)
    #组件component在输出组件中的所有输出位都是可用的，则该输出组件被叫做可用输出组件

    return available_output_components

def sort_input_id_links_and_input_bit_positions(input_id_links, input_bit_positions, component, self):
    updated_input_bit_positions = []
    updated_input_id_links = []
    ordered_list = []
    index = 0
    input_id_link_already_visited = []
    for input_id_link in input_id_links:
        component_input_id_link = get_component_from_id(input_id_link, self)
        if input_id_link not in input_id_link_already_visited:
            input_id_link_already_visited.append(input_id_link)
            for position, link_of_component_id_link in enumerate(component_input_id_link.input_id_links):
                if link_of_component_id_link == component.id:
                    if len(ordered_list) == 0:
                        l = component_input_id_link.input_bit_positions[position]
                        if l != sorted(l):
                            l_ordered = find_correct_order_for_inversion(l, input_bit_positions[index],
                                                                         component_input_id_link)
                        else:
                            l_ordered = input_bit_positions[index]
                        ordered_list.append(l)
                        updated_input_bit_positions.append(l_ordered)
                        updated_input_id_links.append(input_id_links[index])
                    else:
                        position_to_insert = 0
                        first_index = component_input_id_link.input_bit_positions[position][0]
                        for list in ordered_list:
                            if first_index > list[0]:
                                position_to_insert += 1
                            else:
                                break
                        ordered_list.insert(position_to_insert, component_input_id_link.input_bit_positions[position])
                        l = component_input_id_link.input_bit_positions[position]
                        if l != sorted(l):
                            l_ordered = find_correct_order_for_inversion(l, input_bit_positions[index],
                                                                         component_input_id_link)
                        else:
                            l_ordered = input_bit_positions[index]
                        updated_input_bit_positions.insert(position_to_insert, l_ordered)
                        updated_input_id_links.insert(position_to_insert, input_id_links[index])
                    index += 1
    return updated_input_id_links, updated_input_bit_positions

def is_bit_adjacent_to_list_of_bits(bit_name, list_of_bit_names, all_equivalent_bits): 
    if bit_name not in all_equivalent_bits.keys():    #bit_name存在等效位,并且list_of_bit_names中存在bit_name的等效位
        return False
    for name in list_of_bit_names:
        if name in all_equivalent_bits[bit_name]:
            return True
    return False

def equivalent_bits_in_common(bits_of_an_output_component, component_bits, all_equivalent_bits):  
    bits_in_common = []
    n=0
    for bit1 in bits_of_an_output_component:
        bit_name1 = bit1["component_id"] + "_" + str(bit1["position"]) + "_" + bit1["type"]
        # print("bit_name1:",bit_name1)
        if bit_name1 not in all_equivalent_bits.keys():
            # print("no equivalent:",1)
            return []
        # n = 0
        # if bit1["component_id"]=='xor_1_32':
        #         if n == 0 :
        #             print(bit_name1)
        #             n+=1
        #             print(all_equivalent_bits[bit_name1])
        # if bit1["component_id"]=='xor_2_30':
        #         if n == 0 :
        #             print(bit_name1)
        #             n+=1
        #         print(all_equivalent_bits[bit_name1])
        for bit2 in component_bits:
            bit_name2 = bit2["component_id"] + "_" + str(bit2["position"]) + "_" + bit2["type"]
            # print("bit_name2:",bit_name2)
            # if n==0: 
            #     print("equivalent_bits:",bit_name1,bit_name2)
            #     n+=1
            if bit_name2 in all_equivalent_bits[bit_name1]:
                bits_in_common.append(bit1)
                break
    # print("no equivalent:",2)
    # print("len(bits_in_common):",len(bits_in_common))
    return bits_in_common  #返回bits_of_an_output_component中，能够与component_bits中的值相互等价的，bit值

def compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(component,
                                                                                                          available_output_components,
                                                                                                          all_equivalent_bits,
                                                                                                          self, KSA=False):
    #available_output_components是component的可用输出组件
    tmp_input_id_links = []
    tmp_input_bit_positions = []
    # print(component.output_bit_size)
    # print(len(available_output_components))
    # for i in range(len(available_output_components)):
    #     print(available_output_components[i].id)
    for bit_position in range(component.output_bit_size):
        bit_name_input = component.id + "_" + str(bit_position) + "_output"
        flag_link_found = False
        for c in available_output_components:
            # print("available_output_components_id:",c.id)
            if is_possibly_invertible_component(c):
                starting_bit_position = 0
                l = []   #按照input_id_links，记录c中哪一段的bits_position是由component输入的
                for index, link in enumerate(c.input_id_links):  #l存储输出组件中，原组件输入进输出组件的比特位置
                    if link == component.id:    
                        l += list(range(starting_bit_position, starting_bit_position + len(c.input_bit_positions[index])))
                    starting_bit_position += len(c.input_bit_positions[index])
                    # print(link)
                # print("l:",l)
                for i in l:                                              #先因为c的输入比特和component的输出比特存在等价关系，
                    bit_name = c.id + "_" + str(i) + "_input"            #再判断c的输出output_updated和component的输出比特是否有等价关系
                    if is_bit_adjacent_to_list_of_bits(bit_name_input, [bit_name], all_equivalent_bits): #判断原组件的输出比特和输出组件的输入比特是否存在等价关系
                        # print(1)
                        if c.input_bit_size == c.output_bit_size:
                            bit_name_output_updated = c.id + "_" + str(i) + "_output_updated"   
                            if is_bit_adjacent_to_list_of_bits(bit_name, [bit_name_output_updated],
                                                               all_equivalent_bits):
                                #判断输出组件相同位置的input_bit和output_updated_bit之间是否存在等价关系
                                tmp_input_id_links.append(c.id)
                                tmp_input_bit_positions.append(i)
                                flag_link_found = True
                                #input_bit和output_updated_bit之间的等价关系是由函数update_output_bits决定的
                                #经过函数component_inverse得到的逆组件，input和output_updated之间建立等价关系
                                #if条件相当于判断组件c是否是由函数component_inverse得到的组件
                                #如果if成立，则表示原组件的输出比特和输出组件的output_updated比特存在等价关系，将输出组件加入input_id_links候选
                                break
                        else:
                            # print(2)
                            for j in range(c.output_bit_size):
                                bit_name_output_updated = c.id + "_" + str(j) + "_output_updated"
                                if is_bit_adjacent_to_list_of_bits(bit_name, [bit_name_output_updated],
                                                                   all_equivalent_bits):
                                    tmp_input_id_links.append(c.id)
                                    tmp_input_bit_positions.append(j)
                                    flag_link_found = True
                                    #判断输出组件第i位的input_bit和输出组件第j位的output_updated_bit之间是否存在等价关系
                                    break
                            if flag_link_found:
                                break
                if flag_link_found:
                    break

    input_id_links = []                 #按照tmp_input_id_links,构建相关的input_id_links, input_bit_positions
    input_bit_positions = []
    # print(component.id)
    # print(tmp_input_id_links)
    pivot = tmp_input_id_links[0]
    input_bit_position_of_pivot = []
    input_id_links.append(pivot)
    for index, link in enumerate(tmp_input_id_links):
        if link == pivot:
            input_bit_position_of_pivot.append(tmp_input_bit_positions[index])
        else:
            input_bit_positions.append(input_bit_position_of_pivot)
            pivot = link
            input_id_links.append(pivot)
            input_bit_position_of_pivot = []
            input_bit_position_of_pivot.append(tmp_input_bit_positions[index])
    input_bit_positions.append(input_bit_position_of_pivot)
    #根据available_output_component，找到可用于求逆的输出组件和输出组件的序列

    return input_id_links, input_bit_positions

def get_all_bit_names(self,KSA=False):
    dictio = {}
    cipher_components = get_cipher_components(self)
    for c in cipher_components:
        if c.type != INTERMEDIATE_OUTPUT:
            starting_bit_position = 0
            for index, input_id_link in enumerate(c.input_id_links):
                j = 0
                for i in c.input_bit_positions[index]:          #将c的第i块的输入bit重新命名为output_bit
                    output_bit = {                              #表示上一个组件[input_id_link]的输出，进入当前组件c
                        "component_id": input_id_link,
                        "position": i,
                        "type": "output"
                    }
                    output_bit_name = input_id_link + "_" + str(i) + "_output"
                    input_bit = {                               #将c的输入重命名为input_bit
                        "component_id": c.id,
                        "position": starting_bit_position + j,
                        "type": "input"
                    }
                    input_bit_name = c.id + "_" + str(starting_bit_position + j) + "_input"
                    if output_bit_name not in dictio.keys():
                        dictio[output_bit_name] = output_bit
                    if input_bit_name not in dictio.keys():
                        dictio[input_bit_name] = input_bit

                    if c.type != CIPHER_OUTPUT:# and KSA==False:         #CIPHER_OUTPUT不存在逆组件,因此不存在output_updated
                        output_updated_bit = {
                            "component_id": input_id_link,
                            "position": i,
                            "type": "output_updated"
                        }
                        output_updated_bit_name = input_id_link + "_" + str(i) + "_output_updated"
                    else:
                        output_updated_bit = {
                            "component_id": c.id,
                            "position": starting_bit_position + j,
                            "type": "output_updated"
                        }
                        output_updated_bit_name = c.id + "_" + str(starting_bit_position + j) + "_output_updated"
                    # if c.description != INPUT_KEY and KSA == True:
                    #     output_updated_bit = {
                    #         "component_id": input_id_link,
                    #         "position": i,
                    #         "type": "output_updated"
                    #     }
                    #     output_updated_bit_name = input_id_link + "_" + str(i) + "_output_updated"
                    # else:
                    #     output_updated_bit = {
                    #         "component_id": c.id,
                    #         "position": starting_bit_position + j,
                    #         "type": "output_updated"
                    #     }
                    #     output_updated_bit_name = c.id + "_" + str(starting_bit_position + j) + "_output_updated"
                    if output_updated_bit_name not in dictio.keys(): # changed, if added
                        dictio[output_updated_bit_name] = output_updated_bit
                    j += 1
                starting_bit_position += len(c.input_bit_positions[index])

    return dictio

def get_all_bit_names_KSA(self):
    dictio = {}
    cipher_components = get_cipher_components(self)             #将name和具体的bit做对应
    for c in cipher_components:
        # if c.type != INTERMEDIATE_OUTPUT:
            starting_bit_position = 0
            for index, input_id_link in enumerate(c.input_id_links):
                j = 0
                for i in c.input_bit_positions[index]:          #将c的第i块的输入bit重新命名为output_bit
                    output_bit = {                              #表示上一个组件[input_id_link]的输出，进入当前组件c
                        "component_id": input_id_link,          #每个组件的输入和上个组件的输出，分别加入dictio
                        "position": i,
                        "type": "output"
                    }
                    output_bit_name = input_id_link + "_" + str(i) + "_output"
                    input_bit = {                               #将c的输入重命名为input_bit
                        "component_id": c.id,
                        "position": starting_bit_position + j,
                        "type": "input"
                    }
                    input_bit_name = c.id + "_" + str(starting_bit_position + j) + "_input"
                    if output_bit_name not in dictio.keys():
                        dictio[output_bit_name] = output_bit
                    if input_bit_name not in dictio.keys():
                        dictio[input_bit_name] = input_bit

                    # if c.type != CIPHER_OUTPUT:# and KSA==False:         #CIPHER_OUTPUT不存在逆组件,因此不存在output_updated
                        # if c.description[0]=='XOR':print("xor:",c.id)
                    output_updated_bit = {
                        "component_id": input_id_link,
                        "position": i,
                        "type": "output_updated"
                    }
                    output_updated_bit_name = input_id_link + "_" + str(i) + "_output_updated"
                    if output_updated_bit_name not in dictio.keys(): # changed, if added
                        dictio[output_updated_bit_name] = output_updated_bit
                    # else:
                    if c.type == CIPHER_OUTPUT :
                        output_updated_bit = {
                            "component_id": c.id,
                            "position": starting_bit_position + j,
                            "type": "output_updated"
                        }
                        output_updated_bit_name = c.id + "_" + str(starting_bit_position + j) + "_output_updated"
                   
                    if output_updated_bit_name not in dictio.keys(): # changed, if added
                        dictio[output_updated_bit_name] = output_updated_bit
                    j += 1
                starting_bit_position += len(c.input_bit_positions[index])

    return dictio

def get_all_equivalent_bits(self):
    dictio = {}
    component_list = self.get_all_components()   #不包括潜在的输入组件,如key和plaintext
    for c in component_list:                     #将输入组件的输出和当前组件的输入作为等价bit加入dictio中
        current_bit_position = 0                 #将name之间的关系写入equivalent表中
        for index, input_id_link in enumerate(c.input_id_links):
            if c.type == "constant":
                input_bit_positions = list(range(c.output_bit_size))
            else:
                input_bit_positions = c.input_bit_positions[index]
            for i in input_bit_positions:
                output_bit_name = input_id_link + "_" + str(i) + "_output"
                input_bit_name = c.id + "_" + str(current_bit_position) + "_input"
                current_bit_position += 1
                if output_bit_name not in dictio.keys():
                    dictio[output_bit_name] = []
                dictio[output_bit_name].append(input_bit_name)  #同一个output_bit_name可能有多个等价的input_bit_name

    updated_dictio = {}                    #添加双向的equivalent关系，将存在等价关系的多个bit作为新的表项添加到updated_dictio中
    for key, values in dictio.items():
        updated_dictio[key] = values
        for value in values:
            if value not in dictio.keys():
                updated_dictio[value] = []
            updated_dictio[value].append(key)
            for other_value in values:
                if other_value != value:
                    updated_dictio[value].append(other_value)

    return updated_dictio

def get_equivalent_input_bit_from_output_bit(potential_unwanted_component, base_component, available_bits, all_equivalent_bits, 
                                             key_schedule_components, self, input_id_links_old, input_bit_positions_old, KSA=False):
    #potential_unwanted_component是base_component的输入组件
    # print(KSA)
    if KSA == False:
        all_bit_names = get_all_bit_names(self)   #遍历所有组件，all_bit_names包含了每个组件的input_bit以及其输入组件的output_bit
    else :                                        #以及除了cipher_output组件之外的其他组件的output_updated比特
        all_bit_names = get_all_bit_names_KSA(self)
    potential_unwanted_bits = []
    potential_unwanted_bits_names = []
    input_bit_positions_of_potential_unwanted_component = []
    

    if KSA == False:
        for index, input_id_link in enumerate(base_component.input_id_links):
            if input_id_link == potential_unwanted_component.id:
                if input_id_link in input_id_links_old:
                    index_old = input_id_links_old.index(input_id_link)
                    input_positions = input_bit_positions_old[index_old]
                    if input_positions != base_component.input_bit_positions[index]:
                        input_bit_positions_of_potential_unwanted_component = base_component.input_bit_positions[index]
                else:
                    input_bit_positions_of_potential_unwanted_component = base_component.input_bit_positions[index]
    else:
        for index, input_id_link in enumerate(base_component.input_id_links):
            if input_id_link == potential_unwanted_component.id:
                input_bit_positions_of_potential_unwanted_component = base_component.input_bit_positions[index]

    # print('base_component:',base_component.id)
    # print(potential_unwanted_component.id)
    # print(input_bit_positions_of_potential_unwanted_component)
    for i in input_bit_positions_of_potential_unwanted_component:
        output_bit = {
            "component_id": potential_unwanted_component.id,
            "position": i,
            "type": "output"
        }
        output_bit_name = potential_unwanted_component.id + "_" + str(i) + "_output"
        potential_unwanted_bits.append(output_bit)
        potential_unwanted_bits_names.append(output_bit_name)
        
    equivalent_bits = []
    for potential_unwanted_bits_name in potential_unwanted_bits_names:
        for equivalent_bit in all_equivalent_bits[potential_unwanted_bits_name]:
            if (equivalent_bit in all_bit_names.keys()) and (
                    all_bit_names[equivalent_bit]["component_id"] != base_component.id) and (
                    all_bit_names[equivalent_bit] in available_bits) and ( 
                    all_bit_names[equivalent_bit]["component_id"] not in key_schedule_components) and (
                    all_bit_names[equivalent_bit]["type"] == "output_updated"): # changed, line added
                
                # print(equivalent_bit)
                if len(equivalent_bits) == 0:
                    equivalent_bits.append(equivalent_bit)

                elif all_bit_names[equivalent_bit]["component_id"] == all_bit_names[equivalent_bits[0]]["component_id"]:
                    equivalent_bits.append(equivalent_bit)

                elif all_bit_names[equivalent_bit]["component_id"] != all_bit_names[equivalent_bits[0]]["component_id"] and KSA == True:
                    equivalent_bits.append(equivalent_bit)

    if len(equivalent_bits) == 0:
        # print(1)
        return potential_unwanted_component.id, input_bit_positions_of_potential_unwanted_component
    elif KSA==False:
        # print(2)
    # elif KSA==False:
        input_bit_positions = []
        for bit in equivalent_bits:
            input_bit_positions.append(all_bit_names[bit]["position"])
        input_bit_positions.sort()
        # print(input_bit_positions)
        return all_bit_names[equivalent_bits[0]]["component_id"], input_bit_positions
    else :
        # print(3)
        input_bit_positions = []
        input_id_links = []
        number_of_link = 0
        tmp_input_bit_positions = []
        for bit in equivalent_bits:
            if input_id_links==[] or all_bit_names[bit]["component_id"]!=input_id_links[-1]: 
                number_of_link += 1
                input_id_links.append(all_bit_names[bit]["component_id"])
                if input_id_links!=[] and tmp_input_bit_positions != []: input_bit_positions.append(tmp_input_bit_positions)
                tmp_input_bit_positions = []
            tmp_input_bit_positions.append(all_bit_names[bit]["position"])
        if tmp_input_bit_positions!=[]:input_bit_positions.append(tmp_input_bit_positions)
        return input_id_links, input_bit_positions


def compute_input_id_links_and_input_bit_positions_for_inverse_component_from_input_components(component,
                                                                                               available_bits,
                                                                                               all_equivalent_bits,
                                                                                               key_schedule_components,
                                                                                               self,KSA=False):
    input_id_links = []
    input_bit_positions = []
    # if component.description[0] == "XOR": 
    #     print(component.input_id_links)
    for i in range(len(component.input_id_links)):
        number_of_repeats = 0
        component_available = True
        bits = []
        for j in range(len(component.input_bit_positions[i])):
            bit = {
                "component_id": component.input_id_links[i],
                "position": component.input_bit_positions[i][j],
                "type": "output"
            }
            bits.append(bit)
            if not is_bit_contained_in(bit, available_bits):
                component_available = False
                break
            #只要存在一个不可用的输入组件的输入bit就跳出循环，当前输入组件not_available
        # print("component_available:",component_available)
        # print("component_link_id:",component.input_id_links[i])
        if component_available:
            potential_unwanted_component = get_component_from_id(component.input_id_links[i], self)
            equivalent_component, input_bit_positions_of_equivalent_component = get_equivalent_input_bit_from_output_bit(
                potential_unwanted_component, component, available_bits, all_equivalent_bits, key_schedule_components,
                self, input_id_links,input_bit_positions, KSA)
            
            # print("equivalent_component:",equivalent_component)
            if KSA==True and isinstance(equivalent_component, list):
                if input_id_links == []:
                    input_id_links = equivalent_component
                else:
                    input_id_links.extend(equivalent_component)
                # print(1)
                # print(input_id_links[0])
                if input_bit_positions ==[]:
                    input_bit_positions = input_bit_positions_of_equivalent_component
                else :
                    input_bit_positions.extend(input_bit_positions_of_equivalent_component)
            else:
                input_id_links.append(equivalent_component)
                # print(2)
                # print(equivalent_component)
                input_bit_positions.append(input_bit_positions_of_equivalent_component)

    # print("input_id_links:",input_id_links)
    # print("input_bit_positions:",input_bit_positions)
    # print(input_id_links,input_bit_positions)

    return input_id_links, input_bit_positions


def component_input_bits(component):         #将组件component的输入比特,表示为输入组件的output_updated比特
    component_input_bits_list = []           #将输入组件的逆输出和component的输入联系起来
    for index, link in enumerate(component.input_id_links):
        tmp = []
        for position in component.input_bit_positions[index]:
            tmp.append(
                {
                    "component_id": link,       #表示输入组件输入到原组件的比特
                    "position": position,       #将原组件取逆之后，这些比特将会成为输入组件的输入比特
                    "type": "output_updated"    #
                }
            )
        component_input_bits_list.append(tmp)
    return component_input_bits_list     #组件component的link的逆输出比特

def component_output_bits(component, self):    #将组件component的输出比特,表示为output_updated比特
    # set of list_bits needed to invert        #两个方向表示output_updated比特,一个是从组件自身的output来标记,一个是从输出组件的输入比特来标记
    output_components = get_output_components(component, self)
    component_output_bits_list = []
    for c in output_components:
        tmp = []
        for j in range(c.output_bit_size):
            bit = {
                "component_id": c.id,
                "position": j,
                "type": "output_updated"
            }
            tmp.append(bit)
        component_output_bits_list.append(tmp)
    return component_output_bits_list   #组件component的输出组件的逆输出比特

def are_these_bits_available(bits_list, available_bits):
    for bit in bits_list:
        if bit not in available_bits:
            return False
    return True

# def are_there_enough_available_inputs_to_evaluate_component(component, available_bits, all_equivalent_bits, key_schedule_components,
#                 self):
#     #  check input links
#     component_input_bits_list = component_input_bits(component)
#     can_be_evaluated = [True] * len(component_input_bits_list)
#     if component.type == "constant":
#         return False
#     if component.type == "cipher_input":
#         return False
#     for index, bits_list in enumerate(component_input_bits_list):
#         if not are_these_bits_available(bits_list, available_bits):
#             can_be_evaluated[index] = False
#
#     if sum(can_be_evaluated) == len(can_be_evaluated):
#         return True
#     else:
#         for index, link in enumerate(component.input_id_links):
#             if not can_be_evaluated[index]:
#                 component_of_link = get_component_from_id(link, self)
#                 output_components = get_output_components(component_of_link, self)
#                 link_bit_names = []
#                 for bit in component_input_bits_list[index]:
#                     link_bit_name = bit["component_id"] + "_" + str(bit["position"]) + "_output"
#                     link_bit_names.append(link_bit_name)
#                 for output_component in output_components:
#                     if (output_component.id not in component.input_id_links) and (
#                             output_component.id != component.id):
#                         index_id = output_component.input_id_links.index(link)
#                         starting_bit = 0
#                         for index_list, list_bit_positions in enumerate(output_component.input_bit_positions):
#                             if index_list == index_id:
#                                 break
#                             starting_bit += len(list_bit_positions)
#                         output_component_bit_name = output_component.id + "_" + str(starting_bit) + "_output_updated"
#                         if is_bit_adjacent_to_list_of_bits(output_component_bit_name, link_bit_names,
#                                                            all_equivalent_bits):
#                             can_be_evaluated[index] = True
#         return sum(can_be_evaluated) == len(can_be_evaluated)

def are_there_enough_available_inputs_to_evaluate_component(component, available_bits, all_equivalent_bits, key_schedule_components, self):
    #  check input links
    component_input_bits_list = component_input_bits(component)  #获得组件component的输入组件的output_updated序列
    can_be_evaluated = [True] * len(component_input_bits_list)
    available_output_components = []
    if component.type in [CONSTANT, CIPHER_INPUT]:
        # print("False1")
        return False
    for index, bits_list in enumerate(component_input_bits_list):
        if not are_these_bits_available(bits_list, available_bits):
            can_be_evaluated[index] = False
        # print(can_be_evaluated[index])
    available_input_components = [get_component_from_id(c_id, self) for i,c_id in enumerate(component.input_id_links) if can_be_evaluated[i] == True]
    #保存component所有可用的输入组件的id

    if sum(can_be_evaluated) == len(can_be_evaluated):  #如果所有的输入组件和输入bit都available，则该组件能够被等价
        # print("True1")
        # print(component.id)
        return True
    else:  #无法只依靠输入组件来将组件变得等价
        #将component的输入组件link的output_bit，与link的输出组件output_component的output_updated_bit，尝试找出其中的等价关系
        #如果存在等价关系，则将output_component加入available_output_components中。
        for index, link in enumerate(component.input_id_links):
            if not can_be_evaluated[index]:
                component_of_link = get_component_from_id(link, self)
                output_components = get_output_components(component_of_link, self)
                # can_be_evaluated_from_outputs = [False] * len(output_components)
                link_bit_names = []
                for bit in component_input_bits_list[index]:  #将component输入组件的output_updated改成output，也就是component_of_link
                    link_bit_name = bit["component_id"] + "_" + str(bit["position"]) + "_output"  
                    # print(link_bit_name)
                    link_bit_names.append(link_bit_name)
                for index_output_comp, output_component in enumerate(output_components):
                    if (output_component.id not in component.input_id_links) and (
                            output_component.id != component.id):
                        # print(output_component.id)
                        index_id = output_component.input_id_links.index(link)  #output_component的输入中,link在第几位
                        starting_bit = 0
                        for index_list, list_bit_positions in enumerate(output_component.input_bit_positions):
                            if index_list == index_id:
                                break
                            if starting_bit + len(list_bit_positions) < output_component.output_bit_size:
                                starting_bit += len(list_bit_positions)  #计算link的输入bit在output_component输入中的开始位置
                        output_component_bit_name = output_component.id + "_" + str(starting_bit) + "_output_updated"
                        # print(output_component_bit_name)
                        if is_bit_adjacent_to_list_of_bits(output_component_bit_name, link_bit_names,
                                                           all_equivalent_bits):
                            #link的输出比特，在equivalent_bits中，能够与output_component_bit_name等价
                            # can_be_evaluated[index] = True
                            available_output_components.append(output_component)

        list_of_bit_names = []  #假如output_updated_bit和output_bit之间存在等价关系，则当input_bit和output_updated_bit存在关系，则可以间接推导出output
        for c in available_output_components:
            for i in range(c.output_bit_size):
                list_of_bit_names.append(c.id + "_" + str(i) + "_output_updated")  #用于替换link的输出
        for c in available_input_components:
            for i in range(c.output_bit_size):
                list_of_bit_names.append(c.id + "_" + str(i) + "_output")
        for i in range(component.input_bit_size):
            bit_name = component.id + "_" + str(i) + "_input"
            if not is_bit_adjacent_to_list_of_bits(bit_name, list_of_bit_names, all_equivalent_bits):
                # print("False2")
                return False
        # print("True2")
        return True
    #当输入组件的available_bit不够用时，转而使用输入组件link的其他输出组件ouput_component，用他来代替缺失的输入组件的available_bit


def _get_successor_components(component_id, cipher):   #判断该组件是否还有后继,也就是是否是最后一个组件
    graph_cipher = create_networkx_graph_from_input_ids(cipher)
    return list(graph_cipher.successors(component_id))

def are_there_enough_available_inputs_to_perform_inversion(component, available_bits, all_equivalent_bits, self, KSA=False):
    """
    NOTE: it assumes that the component input size is a multiple of the output size
    """
    # STEP 1 - Special case for output components which have no output links (only cipher output)
    if (component.type == CIPHER_OUTPUT) or (component.id == INPUT_KEY):
        return True
    # if component.type == INTERMEDIATE_OUTPUT:
        # print('id:',component.id)
        # print('component.type:',component.type)
        # print(_get_successor_components(component.id, self))
        # print(component.type == INTERMEDIATE_OUTPUT and _get_successor_components(component.id, self)==[])
    if (component.type == INTERMEDIATE_OUTPUT and _get_successor_components(component.id, self) == []):
        return False

    # STEP 2 - Other components
    bit_lists_link_to_component_from_output = component_output_bits(component, self)   #获得当前组件c的所有输出组件的output_updated_bit序列
    # print("len(bit_lists_link_to_component_from_output):",len(bit_lists_link_to_component_from_output))
    component_output_bits_list = []
    for i in range(component.output_bit_size):
        component_output_bits_list.append({"component_id" : component.id, "position" : i, "type" : "output"})
    # if(component.id =='xor_0_35'):print(component_output_bits_list)
    bit_lists_link_to_component_from_output_and_available = []
    for bit_list in bit_lists_link_to_component_from_output:
        # print("bit_list_id:",bit_list[0]["component_id"],len(bit_list))
        bits_in_common = equivalent_bits_in_common(bit_list, component_output_bits_list, all_equivalent_bits)
        # print("bits_in_common:",bits_in_common)
        #返回bit_list中，能够与component_output_bits_list中的值相互等价的，bit值
        #返回输出组件的output_updated_bit中，能够与当前组件的output_bit相互等价的bit
        # print("bit_list_id:",bit_list[0]["component_id"],len(bit_list),"bits_in_common==[]",bits_in_common==[])
        # if(component.id == 'xor_0_35'): print(bits_in_common)
        for bit in bits_in_common:
            if bit in available_bits:
                bit_lists_link_to_component_from_output_and_available.append(bit)  
                #返回component中，可用的输出bit，并且和输出组件的output_updated存在等价关系
        
    # print("len(bit_lists_link_to_component_from_output_and_available):",len(bit_lists_link_to_component_from_output_and_available))

    # handling available bits from inputs
    bit_lists_link_to_component_from_input = component_input_bits(component)
    #获得当前组件c的所有输入组件的输入位置bit序列以及对应的output_updated_bit值
    # if bit_lists_link_to_component_from_input==[]:
    #     for i in range(len(bit_lists_link_to_component_from_input)):
    #         print(bit_lists_link_to_component_from_input[i][0])
    # if component.id == 'xor_1_54': 
    #     print(bit_lists_link_to_component_from_input)
    can_be_used_for_inversion = [True] * len(bit_lists_link_to_component_from_input)
    for index, bits_list in enumerate(bit_lists_link_to_component_from_input):
        if not are_these_bits_available(bits_list, available_bits):
            can_be_used_for_inversion[index] = False
        # print("can_be_used_for_inversion_before:",can_be_used_for_inversion[index])
    
    # if component.id == 'xor_2_29': 
    #     print(can_be_used_for_inversion[0],can_be_used_for_inversion[1])
    for index, link in enumerate(component.input_id_links):
        # print("link:",link)
        if not can_be_used_for_inversion[index]:
            component_of_link = get_component_from_id(link, self)
            # print("component_of_link:",component_of_link.id)
            output_components = get_output_components(component_of_link, self)    #output_components包含component,但不只是component
            link_bit_names = []
            for bit in bit_lists_link_to_component_from_input[index]:
                link_bit_name = bit["component_id"] + "_" + str(bit["position"]) + "_output"
                link_bit_names.append(link_bit_name)         #存储component_input_bits得到的所有bit的output版本
            for output_component in output_components:
                nb_available_output_component_bits = 0
                if ((output_component.id not in component.input_id_links) and (
                        output_component.id != component.id) and (output_component.type != INTERMEDIATE_OUTPUT)) or(
                        (output_component.id not in component.input_id_links) and (
                        output_component.id != component.id) and (KSA ==True)
                        ):
                    # if component.id == 'xor_2_28':print('xor_2_28 output_componrnt_id:',output_component.id,'xor_2_28 link_id:',link)
                    # if component.id == 'xor_1_33':print('xor_1_33 output_componrnt_id:',output_component.id,'xor_1_33 link_id:',link)
                    # if component.id == 'xor_0_35':print('xor_0_35 output_componrnt_id:',output_component.id,'xor_0_35 link_id:',link)
                    # if component.id == 'xor_1_54':print('xor_0_35 output_componrnt_id:',output_component.id,'xor_1_54 link_id:',link)
                    for i in range(output_component.output_bit_size):
                        output_component_bit_name = output_component.id + "_" + str(i) + "_output_updated" #构建link和component其他输出组件之间的关系
                        output_component_bit = {"component_id": output_component.id, "position": i, "type": "output_updated"}
                        if is_bit_adjacent_to_list_of_bits(output_component_bit_name, link_bit_names, all_equivalent_bits) and (output_component_bit in available_bits):
                            nb_available_output_component_bits += 1    #如果output_component_bit和link_bit的bit存在等价关系,并且可用,那么+1
                    # print(output_component.id,nb_available_output_component_bits)
                    # print()
                    # print("nb_available_output_component_bits:",nb_available_output_component_bits)
                    if nb_available_output_component_bits == output_component.output_bit_size:
                        can_be_used_for_inversion[index] = True
                    elif nb_available_output_component_bits == component_of_link.output_bit_size and KSA==True:
                        can_be_used_for_inversion[index]= True

    # for index, bits_list in enumerate(bit_lists_link_to_component_from_input):
        # print("can_be_used_for_inversion:",can_be_used_for_inversion[index])
    # print()

    # if component.id == 'xor_1_54': 
    #     print(can_be_used_for_inversion[0],can_be_used_for_inversion[1])
    # Merging available bits from inputs and output
    bit_lists_link_to_component_from_input_and_output = bit_lists_link_to_component_from_output_and_available
    # print("len(bit_lists_link_to_component_from_input_and_output):",len(bit_lists_link_to_component_from_input_and_output))
    for index, bits_list in enumerate(bit_lists_link_to_component_from_input):
        # print("can_be_used_for_inversion:",can_be_used_for_inversion[index])
        if can_be_used_for_inversion[index]:
            bit_lists_link_to_component_from_input_and_output += bits_list
    # print("len(bit_lists_link_to_component_from_input_and_output):",len(bit_lists_link_to_component_from_input_and_output))

    if component.id == INPUT_PLAINTEXT or INTERMEDIATE_OUTPUT in component.id:
        return len(bit_lists_link_to_component_from_input_and_output) >= component.output_bit_size
    else:
        # print("component.input_bit_size:",component.input_bit_size)
        # print("len(bit_lists_link_to_component_from_input_and_output):",len(bit_lists_link_to_component_from_input_and_output))
        return len(bit_lists_link_to_component_from_input_and_output) >= component.input_bit_size

def is_possibly_invertible_component(component):  #从分类上看component是否可逆

    # if sbox is a permutation
    if component.type == SBOX and \
            len(list(set(component.description))) == len(component.description):
        is_invertible = True
    # if sbox is NOT a permutation, then cannot be inverted
    elif component.type == SBOX and len(list(set(component.description))) != len(component.description):
        is_invertible = False
    elif component.type == LINEAR_LAYER:
        is_invertible = True
    elif component.type == MIX_COLUMN:
        is_invertible = True
    # for rotations and shift rows
    elif component.type == WORD_OPERATION and component.description[0] == "ROTATE":
        is_invertible = True
    elif component.type == CONSTANT:
        is_invertible = True
    elif component.type == WORD_OPERATION and component.description[0] == "SHIFT":
        is_invertible = False
    elif component.type == WORD_OPERATION and component.description[0] == "XOR":
        is_invertible = True
    elif component.type == WORD_OPERATION and component.description[0] == "SIGMA":
        is_invertible = True
    elif component.type == WORD_OPERATION and component.description[0] == "MODADD":
        is_invertible = True
    elif component.type == WORD_OPERATION and component.description[0] == "OR":
        is_invertible = False
    elif component.type == WORD_OPERATION and component.description[0] == "AND":
        is_invertible = False
    elif component.type == WORD_OPERATION and component.description[0] == "NOT":
        is_invertible = True
    elif component.type in [CIPHER_INPUT, CIPHER_OUTPUT, INTERMEDIATE_OUTPUT]:
        is_invertible = True
    else:
        is_invertible = False

    return is_invertible

def is_intersection_of_input_id_links_null(inverse_component, component):
    #判断原组件和逆组件的input_id_links交集是否为空
    flag_intersection_null = True
    for input_id_link in component.input_id_links:
        if input_id_link in inverse_component.input_id_links:
            flag_intersection_null = False
            #如果原组件和逆组件拥有同样的输入组件，则flag为false
    if flag_intersection_null:
        return True, []

    if (component.type == "constant"):
        return False, list(range(component.output_bit_size))

    starting_bit_position = 0
    input_bit_positions = []
    for index, input_id_link in enumerate(component.input_id_links):
        if input_id_link not in inverse_component.input_id_links:
            input_bit_positions += range(starting_bit_position, starting_bit_position + len(component.input_bit_positions[index]))
        starting_bit_position += len(component.input_bit_positions[index])
    #返回的input_bit_position为component中，与inverse_component不同的input_id_links的输入位置
    return False, input_bit_positions

def find_input_id_link_bits_equivalent(inverse_component, component, all_equivalent_bits,available_bits,KSA=False):
    #默认component和inverse_component相同位置的input_id_link是存在关系的，
    #但是两个组件的input_id_links数量并不一定相等，因此上述情景是否成立存疑
    #component的input_id_link数量是基本上小于inverse_component的input_id_links数量的
    starting_bit_position = 0
    for index, input_id_link in enumerate(component.input_id_links):
        # if component.id =='xor_1_33':
        #     print("input_id_links:",component.input_id_links)
        #     print("inverse_input_id_links:",inverse_component.input_id_links)
        # if component.id =='xor_2_28':
        #     print("input_id_links:",component.input_id_links)
        #     print("inverse_input_id_links:",inverse_component.input_id_links)            
        input_bit_positions_of_inverse = inverse_component.input_bit_positions[index]
        for position, i in enumerate(component.input_bit_positions[index]):
            # print("starting_bit_position:",starting_bit_position)
            # print("num")
            input_bit_name = input_id_link + "_" + str(i) + "_output"
            #逆组件的input_id_link可能是原组件的输出，也可能原组件的输入组件的其他输出组件，还有可能是原组件的输入组件的output_bit的等价bit序列
            potential_equivalent_bit_name = inverse_component.input_id_links[index] + "_" + str(
                input_bit_positions_of_inverse[position]) + "_input"
            if input_bit_name not in all_equivalent_bits[potential_equivalent_bit_name] and KSA == False:  
                input_bit_positions = list(
                    range(starting_bit_position, starting_bit_position + len(component.input_bit_positions[index])))
                return input_bit_positions
            elif input_bit_name not in all_equivalent_bits[potential_equivalent_bit_name] and KSA == True:

                flag = False
                input_bit_positions = list(
                    range(starting_bit_position, starting_bit_position + len(component.input_bit_positions[index])))

                input_bit_name = component.id + "_" + str(input_bit_positions[0]) + "_input"
                # print(potential_equivalent_bit_name)
                # if (potential_equivalent_bit_name == 'xor_2_27_0_input'): print(all_equivalent_bits["xor_2_27_32_input"])
                # print( potential_equivalent_bit_name in all_equivalent_bits.keys())
                # print(all_equivalent_bits[potential_equivalent_bit_name])
                for ind,ele in enumerate(all_equivalent_bits[input_bit_name]):
                    
                    partial = ele.split('_')
                    if partial[-1]=='updated' and partial[-2] == 'output' and partial[0] !='intermediate':
                        flag = True
                # print("flag:",flag)
                if flag == False:
                    # print("starting_bit_position:",starting_bit_position)
                    input_bit_positions = list(
                    range(starting_bit_position, starting_bit_position + len(component.input_bit_positions[index])))
                    return input_bit_positions
                elif index==len(component.input_id_links)-1:
                    input_bit_positions = list(
                    range(starting_bit_position, starting_bit_position + len(component.input_bit_positions[index])))
                    return input_bit_positions
                else :
                    break
        starting_bit_position += len(component.input_bit_positions[index])
    raise ValueError("Equivalent bits not found")

def update_output_bits(inverse_component, self, all_equivalent_bits, available_bits,KSA=False):
    #将当前组件的output_updated_bit加入到availabel_bit中，同时在equivale_bit中添加等价关系

    def _add_output_bit_equivalences(id, bit_positions, component, all_equivalent_bits, available_bits):
        for i in range(component.output_bit_size):
            output_bit_name_updated = id + "_" + str(i) + "_output_updated"     #组件求逆之后输入输出大小不变
            bit = {                                                             #因此output_updated大小为原本的output大小
                "component_id": id,
                "position": i,
                "type": "output_updated"
            }
            available_bits.append(bit)
            input_bit_name = id + "_" + str(bit_positions[i]) + "_input"
            all_equivalent_bits[input_bit_name].append(output_bit_name_updated)   #当前组件的output_updated_bit和input_bit构建等价关系
            if output_bit_name_updated not in all_equivalent_bits.keys():         #不会设计到其他组件
                all_equivalent_bits[output_bit_name_updated] = []
            all_equivalent_bits[output_bit_name_updated].append(input_bit_name)
            for name in all_equivalent_bits[input_bit_name]:
                if name != output_bit_name_updated:
                    all_equivalent_bits[output_bit_name_updated].append(name)
                    all_equivalent_bits[name].append(output_bit_name_updated)

    id = inverse_component.id
    component = get_component_from_id(id, self)
    flag_is_intersection_of_input_id_links_null, input_bit_positions = is_intersection_of_input_id_links_null(
        inverse_component, component)
    #flag表示原组件和逆组件的input_id_links是否存在交集，input_bit_positions表示原组件中，与逆组件不同的input_id_links的输入位置

    if (component.description == [INPUT_KEY]) or (component.description == [INPUT_TWEAK]) or(component.type == CONSTANT):
        #上述几个类型的component不存在evaluated_component，但是存在inverse_component
        #这几个inverse_component与一般的evaluated_component类似，令output_bit和output_updated_bit相互等价
        for i in range(component.output_bit_size):   #如果component是key或者tweak或者constant,则将其相同位置的输入位和输出位设置为等价位
            output_bit_name_updated = id + "_" + str(i) + "_output_updated"
            bit = {
                "component_id": id,
                "position": i,
                "type": "output_updated"    #key、tewakkey、常数不存在输入，因此没有input_bit
            }
            available_bits.append(bit)
            input_bit_name = id + "_" + str(i) + "_output"   #以output为输入,以output_updated为输出,此处使用逆组件的id,实际上就是原组件的id
            if input_bit_name not in all_equivalent_bits.keys(): #构建inverse_component的output_updated_bit和output_bit的等价关系
                all_equivalent_bits[input_bit_name] = []
            all_equivalent_bits[input_bit_name].append(output_bit_name_updated)
            if output_bit_name_updated not in all_equivalent_bits.keys():
                all_equivalent_bits[output_bit_name_updated] = []
            all_equivalent_bits[output_bit_name_updated].append(input_bit_name)
            for name in all_equivalent_bits[input_bit_name]:
                if name != output_bit_name_updated:
                    all_equivalent_bits[output_bit_name_updated].append(name)
    elif component.input_bit_size == component.output_bit_size:
        _add_output_bit_equivalences(id, range(component.output_bit_size), component, all_equivalent_bits, available_bits)
    else:
        if flag_is_intersection_of_input_id_links_null:
            input_bit_positions = find_input_id_link_bits_equivalent(inverse_component, component, all_equivalent_bits,available_bits,KSA)
            #input_bit_positions大小为component的output_bit_size
            # if component.id == 'xor_1_34': print(input_bit_positions)
        _add_output_bit_equivalences(id, input_bit_positions, component, all_equivalent_bits, available_bits)
        output_bit_name_updated = id + "_" + str(0) + "_output_updated"
        # print("id:",id,",",output_bit_name_updated,"equivalent_bits",all_equivalent_bits[output_bit_name_updated])

def order_input_id_links_for_modadd(component, input_id_links, input_bit_positions, available_bits, self):
    available_output_components_with_indices = get_available_output_components(component, available_bits, self, True)

    old_index = 0
    for index, input_id_link in enumerate(input_id_links):
        index_id_list = [_ for _, x in enumerate(available_output_components_with_indices) if
                         x[0].id == input_id_link and set(x[1]) == set(input_bit_positions[index])]
        if index_id_list:
            old_index = index
            break
    input_id_links.insert(0, input_id_links.pop(old_index))
    input_bit_positions.insert(0, input_bit_positions.pop(old_index))
    return input_id_links, input_bit_positions

def component_inverse(component, available_bits, all_equivalent_bits, key_schedule_components, self,KSA=False):
    """
    This functions assumes that the component is actually invertible.
    """
    #组件求逆，但他的输入大小，输出大小以及id都是不变的
    output_components = get_output_components(component, self)  #component
    available_output_components = get_available_output_components(component, available_bits, self)
    # print("num of available_output_components:",len(available_output_components))
    # if (available_output_components!=[]):
    #     for _ in range(len(available_output_components)):
    #         print("available_output_components:",(available_output_components[_].id))

    if component.type == SBOX:
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(component, output_components, all_equivalent_bits, self)
        S = SBox(component.description)
        Sinv = list(S.inverse())
        inverse_component = Component(component.id, component.type, Input(component.input_bit_size, input_id_links, input_bit_positions), component.output_bit_size, Sinv)
        inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == LINEAR_LAYER:
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(component, output_components, all_equivalent_bits, self)
        binary_matrix = binary_matrix_of_linear_component(component)
        inv_binary_matrix = binary_matrix.inverse()
        inverse_component = Component(component.id, component.type,
                                      Input(component.input_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, list(inv_binary_matrix))
        inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == MIX_COLUMN:
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(
            component, available_output_components, all_equivalent_bits, self)
        description = component.description
        G = PolynomialRing(GF(2), 'x')
        x = G.gen()
        irr_poly = int_to_poly(int(description[1]), int(description[2]), x)
        if irr_poly and not irr_poly.is_irreducible():
            binary_matrix = binary_matrix_of_linear_component(component)
            inv_binary_matrix = binary_matrix.inverse()
            inverse_component = Component(component.id, LINEAR_LAYER, Input(component.input_bit_size, input_id_links, input_bit_positions), component.output_bit_size, list(inv_binary_matrix.transpose()))
            inverse_component.__class__ = linear_layer_component.LinearLayer
        else:
            inv_matrix = get_inverse_matrix_in_integer_representation(component)
            inverse_component = Component(component.id, component.type,
                                          Input(component.input_bit_size, input_id_links, input_bit_positions),
                                          component.output_bit_size, [[list(row) for row in inv_matrix]] + component.description[1:])
            inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == WORD_OPERATION and component.description[0] == "SIGMA":
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(component, output_components, all_equivalent_bits, self)
        binary_matrix = binary_matrix_of_linear_component(component)
        inv_binary_matrix = binary_matrix.inverse()
        inverse_component = Component(component.id, LINEAR_LAYER,
                                      Input(component.input_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, list(inv_binary_matrix.transpose()))
        inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == WORD_OPERATION and component.description[0] == "XOR" and KSA == False:
        input_id_links_from_output_components, input_bit_positions_from_output_components = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(
            component, available_output_components, all_equivalent_bits, self)
        # print(input_id_links_from_output_components,input_bit_positions_from_output_components)
        
        input_id_links_from_input_components, input_bit_positions_from_input_components = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_input_components(
            component, available_bits, all_equivalent_bits, key_schedule_components, self)
        # print(input_id_links_from_input_components,input_bit_positions_from_input_components)
        
        input_id_links = input_id_links_from_input_components + input_id_links_from_output_components
        input_bit_positions = input_bit_positions_from_input_components + input_bit_positions_from_output_components

        # print(input_id_links,input_bit_positions,component.input_bit_size)
        inverse_component = Component(component.id, component.type,
                                      Input(component.input_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, component.description)
        inverse_component.__class__ = component.__class__
        # print(inverse_component.id,inverse_component.input_bit_positions,inverse_component.input_bit_size)
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == WORD_OPERATION and component.description[0] == "XOR" and KSA == True:
        # if available_output_components!=[]:
        #     print("len_of_available_output_components:",len(available_output_components))
        #     for i in range(len(available_output_components)):
        #         print("available_output_components:",available_output_components[i].id) 
        tmp_output_components = available_output_components.copy()
        # for i in range(len(available_output_components)):
        #     print(available_output_components[i].id)

        # print()
        # print(input_id_links_from_input_components)
        # print(input_id_links_from_output_components)
        # print()
        input_id_links_from_output_components, input_bit_positions_from_output_components = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(
            component, available_output_components, all_equivalent_bits, self,KSA=True)
        # print(input_id_links_from_output_components,input_bit_positions_from_output_components)
        
        input_id_links_from_input_components, input_bit_positions_from_input_components = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_input_components(
            component, available_bits, all_equivalent_bits, key_schedule_components, self,KSA=True)
        input_id_links = input_id_links_from_input_components + input_id_links_from_output_components
        input_bit_positions = input_bit_positions_from_input_components + input_bit_positions_from_output_components

        # print(input_id_links,input_bit_positions,component.input_bit_size)
        inverse_component = Component(component.id, component.type,
                                      Input(component.input_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, component.description)
        inverse_component.__class__ = component.__class__
        # print(inverse_component.id,inverse_component.input_bit_positions,inverse_component.input_bit_size)
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits,KSA)
    elif component.type == WORD_OPERATION and component.description[0] == "ROTATE":
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(component, available_output_components, all_equivalent_bits, self)
        inverse_component = Component(component.id, component.type,
                                      Input(component.input_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, [component.description[0], -component.description[1]])
        # print(component.id, component.input_bit_positions,component.output_bit_size)
        inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == WORD_OPERATION and component.description[0] == "NOT":
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(component, available_output_components, all_equivalent_bits, self)
        inverse_component = Component(component.id, component.type,
                                      Input(component.input_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, [component.description[0], component.description[1]])
        inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == WORD_OPERATION and component.description[0] == "MODADD":
        input_id_links_from_output_components, input_bit_positions_from_output_components = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(
            component, available_output_components, all_equivalent_bits, self)
        input_id_links_from_input_components, input_bit_positions_from_input_components = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_input_components(
            component, available_bits, all_equivalent_bits, key_schedule_components, self)
        input_id_links = input_id_links_from_input_components + input_id_links_from_output_components
        input_bit_positions = input_bit_positions_from_input_components + input_bit_positions_from_output_components
        input_id_links, input_bit_positions = order_input_id_links_for_modadd(component, input_id_links, input_bit_positions, available_bits, self)
        inverse_component = Component(component.id, component.type,
                                      Input(component.input_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, ["MODSUB", component.description[1], component.description[2]])
        inverse_component.__class__ = modsub_component.MODSUB
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == CONSTANT:
        inverse_component = Component(component.id, component.type,
                                      Input(0, [''], [[]]),
                                      component.output_bit_size, component.description)
        inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == CIPHER_OUTPUT:
        inverse_component = Component(component.id, CIPHER_INPUT,
                                      Input(0, [[]], [[]]),
                                      component.output_bit_size, [CIPHER_INPUT])
        setattr(inverse_component, "round", -1)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == CIPHER_INPUT and (component.id in [INPUT_PLAINTEXT, INPUT_STATE] or INTERMEDIATE_OUTPUT in component.id):
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(
            component, available_output_components, all_equivalent_bits, self)
        inverse_component = Component(component.id, CIPHER_OUTPUT,
                                      Input(component.output_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, [component.id])
        inverse_component.__class__ = cipher_output_component.CipherOutput
        setattr(inverse_component, "round", component.round)
    elif component.type == CIPHER_INPUT and (component.description == [INPUT_KEY] or component.id == INPUT_TWEAK) and (KSA==False):
        inverse_component = Component(component.id, CIPHER_INPUT,
                                      Input(0, [[]], [[]]),
                                      component.output_bit_size, [component.id])
        inverse_component.__class__ = component.__class__
        setattr(inverse_component, "round", -1)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    elif component.type == CIPHER_INPUT and (component.description == [INPUT_KEY] or component.id == INPUT_TWEAK) and KSA==True:
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(
            component, available_output_components, all_equivalent_bits, self)
        inverse_component = Component(component.id, CIPHER_OUTPUT,
                                      Input(component.output_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, [component.id])
        inverse_component.__class__ = cipher_output_component.CipherOutput
        # print('inverse_component:',inverse_component.id)
        setattr(inverse_component, "round", component.round)
    elif component.type == INTERMEDIATE_OUTPUT:
        input_id_links, input_bit_positions = compute_input_id_links_and_input_bit_positions_for_inverse_component_from_available_output_components(
            component, available_output_components, all_equivalent_bits, self)
        inverse_component = Component(component.id, INTERMEDIATE_OUTPUT,
                                      Input(component.output_bit_size, input_id_links, input_bit_positions),
                                      component.output_bit_size, component.description)
        inverse_component.__class__ = intermediate_output_component.IntermediateOutput
        setattr(inverse_component, "round", component.round)
        update_output_bits(inverse_component, self, all_equivalent_bits, available_bits)
    else:
        inverse_component = Component("NA", "NA",
                                      Input(0, [[]], [[]]),
                                      component.output_bit_size, ["NA"])

    return inverse_component

def update_available_bits_with_component_output_bits(component, available_bits, cipher):  #将组件component的输出位和输出组件的输入位加入available_bits中

    output_components = get_output_components(component, cipher)

    for i in range(component.output_bit_size):
        bit = {
            "component_id": component.id,
            "position": i,
            "type": "output"
        }
        # if component.id == 'key':
            # print("key3:",component.id)
            # print(available_bits[-1])
        add_bit_to_bit_list(bit, available_bits)
        # if component.id == 'key': print(available_bits[-1])

    # add bits of the connected output components
    for c in output_components:
        accumulator = 0
        for i in range(len(c.input_id_links)):
            if c.input_id_links[i] == component.id:
                for j in range(len(c.input_bit_positions[i])): #c.input_bit_positions[i]表示compont在组件c上的输入的位置序列
                    component_output_bit = {
                        "component_id": component.id,
                        "position": j,
                        "type": "output"
                    }
                    # if component.id == 'key':
                    #     print("key4:",component.id)
                    if is_bit_contained_in(component_output_bit, available_bits):
                        c_input_bit = {
                            "component_id": c.id,
                            "position": accumulator + j,
                            "type": "input"
                        }
                        # if c.id == 'key':
                        #     print("key5:",c.id)
                        add_bit_to_bit_list(c_input_bit, available_bits)
            accumulator += len(c.input_bit_positions[i])
    return


def update_available_bits_with_component_input_bits(component, available_bits): #将组件component的输入位和上流组件的输出位加入available_bits
    for i in range(component.input_bit_size):
        bit = {
            "component_id": component.id,
            "position": i,
            "type": "input"
        }
        add_bit_to_bit_list(bit, available_bits)
        # if component.id == 'key': 
        #     print("key1:",component.id)

    # add bits of the connected input components
    for i in range(len(component.input_id_links)):
        for j in range(len(component.input_bit_positions[i])):
            bit1 = {
                "component_id": component.input_id_links[i],
                "position": component.input_bit_positions[i][j],
                "type": "output"
            }
            add_bit_to_bit_list(bit1, available_bits)
            # if component.input_bit_positions[i] == 'key': 
            #     print("key2:",component.id)
    return


def all_input_bits_available(component, available_bits):
    for i in range(component.input_bit_size):
        bit = {
            "component_id": component.id,
            "position": i,
            "type": "input"
        }
        if not is_bit_contained_in(bit, available_bits):
            return False
    return True

def all_output_updated_bits_available(component, available_bits):    
    for i in range(component.input_bit_size):       #output_updated与input相同,可以认为output_updated是组件求逆之后的输出
        bit = {
            "component_id": component.id,
            "position": i,
            "type": "output_updated"
        }
        if not is_bit_contained_in(bit, available_bits):
            return False
    return True

def all_output_bits_available(component, available_bits):
    #返回当前组件的所有输出output_updated是否都是available的
    for i in range(component.output_bit_size):
        bit = {
            "component_id": component.id,
            "position": i,
            "type": "output_updated"
        }
        if not is_bit_contained_in(bit, available_bits):
            return False
    return True


def get_component_from_id(component_id, self):
    cipher_components = get_cipher_components(self)
    for c in cipher_components:
        if c.id == component_id:
            return c
    return None


def get_key_schedule_component_ids(self):
    key_schedule_component_ids = [input for input in self.inputs if INPUT_KEY in input or INPUT_TWEAK in input]
    component_list = self.get_all_components()
    for c in component_list:
        flag_belong_to_key_schedule = True
        for link in c.input_id_links:
            if link not in key_schedule_component_ids:
                flag_belong_to_key_schedule = False
                break
        if flag_belong_to_key_schedule or (c.type == CONSTANT):
            key_schedule_component_ids.append(c.id)

    return key_schedule_component_ids


def is_output_bits_updated_equivalent_to_input_bits(output_bits_updated_list, input_bits_list, all_equivalent_bits):
    n =0
    for bit in output_bits_updated_list:
        if not is_bit_adjacent_to_list_of_bits(bit, input_bits_list, all_equivalent_bits):
            return False
    return True
#是否输出比特的值都能够于输入比特相互等价

def find_correct_order(id1, list1, id2, list2, component_output_bit_size, all_equivalent_bits):
    list2_ordered = []
    for i in list1:
        bit = id1 + "_" + str(i) + "_output"
        for j in list2:
            bit_potentially_equivalent = id2 + "_" + str(j) + "_input"
            if bit_potentially_equivalent in all_equivalent_bits[bit]:
                list2_ordered.append(j%component_output_bit_size)
                break
    return list2_ordered

def find_correct_order_for_inversion(list1, list2, component):
    list2_ordered = []
    for i in list1:
        list2_ordered.append(list2[i % component.output_bit_size])
    return list2_ordered

# def evaluated_component(component, available_bits, key_schedule_component_ids, all_equivalent_bits, self):
#     input_id_links = []
#     input_bit_positions = []
#     if (component.type == "fdjgfk") and (component.id not in key_schedule_component_ids):
#         for index_link, link in enumerate(component.input_id_links):
#             component_of_link = get_component_from_id(link, self)
#             available_output_components = get_available_output_components(component_of_link, available_bits, self)
#             link_bit_names = []
#             for i in range(component_of_link.output_bit_size):
#                 link_bit_name = link + "_" + str(i) + "_output"
#                 link_bit_names.append(link_bit_name)
#             for index_available_output_component, available_output_component in enumerate(available_output_components):
#                 if (available_output_component.id not in component.input_id_links) and (
#                         available_output_component.id != component.id):
#                     index_id = available_output_component.input_id_links.index(link)
#                     starting_bit = 0
#                     for index_list, list_bit_positions in enumerate(available_output_component.input_bit_positions):
#                         if index_list == index_id:
#                             break
#                         starting_bit += len(list_bit_positions)
#                     available_output_component_bit_name = available_output_component.id + "_" + str(starting_bit) + "_output_updated"
#                     if is_bit_adjacent_to_list_of_bits(available_output_component_bit_name, link_bit_names,
#                                                        all_equivalent_bits):
#                         input_id_links.append(available_output_component.id)
#                         input_bit_positions.append(list(range(starting_bit, starting_bit + len(available_output_component.input_bit_positions[index_list]))))
#
#         evaluated_component = Component(component.id, component.type, Input(component.input_bit_size, input_id_links, input_bit_positions),
#                                         component.output_bit_size, component.description)
#         setattr(evaluated_component, "round", getattr(component, "round"))
#         return evaluated_component
#
#     if component.type != "cipher_input":
#         components_with_same_input_bits = []
#         starting_bit_position = 0
#         for i in range(len(component.input_id_links)):
#             components_with_same_input_bits = get_all_components_with_the_same_input_id_link_and_input_bit_positions(
#                 component.input_id_links[i], component.input_bit_positions[i], self)
#             components_with_same_input_bits.remove(component)
#
#             # check if the original input component has all output bits available
#             original_input_component = get_component_from_id(component.input_id_links[i], self)
#             output_bits_updated_list = []
#             for j in component.input_bit_positions[i]:
#                 output_bit_updated_name = original_input_component.id + "_" + str(j) + "_output_updated"
#                 output_bits_updated_list.append(output_bit_updated_name)
#             input_bits_list = []
#             for k in range(starting_bit_position, starting_bit_position + len(component.input_bit_positions[i])):
#                 input_bit_name = component.id + "_" + str(k) + "_input"
#                 input_bits_list.append(input_bit_name)
#             starting_bit_position += len(component.input_bit_positions[i])
#             flag = is_output_bits_updated_equivalent_to_input_bits(output_bits_updated_list, input_bits_list, all_equivalent_bits)
#             if all_output_bits_available(original_input_component, available_bits) and flag:
#                 input_id_links.append(component.input_id_links[i])
#                 input_bit_positions.append(component.input_bit_positions[i])
#             else:
#                 # select component for which the connected components have all their inputs available
#                 link = component.input_id_links[i]
#                 original_input_bit_positions_of_link = component.input_bit_positions[i]
#                 for c in components_with_same_input_bits:
#                     if all_input_bits_available(c, available_bits):
#                         input_id_links.append(c.id)
#                         # get input bit positions
#                         accumulator = 0 # changed
#                         for j in range(len(c.input_id_links)):
#                             if component.input_id_links[i] == c.input_id_links[j]:
#                                 l = [h for h in range(accumulator, accumulator + len(component.input_bit_positions[i]))]
#                                 l_ordered = find_correct_order(link, original_input_bit_positions_of_link, c.id, l, all_equivalent_bits)
#                                 input_bit_positions.append(l_ordered)
#                                 # break?
#                             else:
#                                 accumulator += len(c.input_bit_positions[j]) # changed
#     else:
#         input_id_links = [[]]
#         input_bit_positions = [[]]
#     evaluated_component = Component(component.id, component.type, Input(component.input_bit_size, input_id_links, input_bit_positions),
#                                     component.output_bit_size, component.description)
#     setattr(evaluated_component, "round", getattr(component, "round"))
#
#     id = component.id
#     for i in range(evaluated_component.output_bit_size):
#         output_bit_name_updated = id + "_" + str(i) + "_output_updated"
#         bit = {
#             "component_id": id,
#             "position": i,
#             "type": "output_updated"
#         }
#         available_bits.append(bit)
#         output_bit_name = id + "_" + str(i) + "_output"
#         if output_bit_name not in all_equivalent_bits.keys():
#             all_equivalent_bits[output_bit_name] = []
#         all_equivalent_bits[output_bit_name].append(output_bit_name_updated)
#         if output_bit_name_updated not in all_equivalent_bits.keys():
#             all_equivalent_bits[output_bit_name_updated] = []
#         all_equivalent_bits[output_bit_name_updated].append(output_bit_name)
#         for name in all_equivalent_bits[output_bit_name]:
#             if name != output_bit_name_updated:
#                 all_equivalent_bits[output_bit_name_updated].append(name)
#
#     return evaluated_component

def evaluated_component(component, available_bits, key_schedule_component_ids, all_equivalent_bits, self,KSA=False ):
    input_id_links = []          #找出component的输入组件的可替换组件,重新构建component的输入组件列表以及输入位置列表,
    input_bit_positions = []     #并将component的等效组件,相关的bit加入available_bits以及all_equivalent_bits

    if component.type != "cipher_input":
        components_with_same_input_bits = []
        starting_bit_position = 0
        for i in range(len(component.input_id_links)):
            components_with_same_input_bits = get_all_components_with_the_same_input_id_link_and_input_bit_positions(
                component.input_id_links[i], component.input_bit_positions[i], self)
            components_with_same_input_bits.remove(component)  #表示和component相同输入的组件列表,但排除了component

            # check if the original input component has all output bits available
            original_input_component = get_component_from_id(component.input_id_links[i], self)  #component的某个输入组件
            output_bits_updated_list = []
            for j in component.input_bit_positions[i]:
                output_bit_updated_name = original_input_component.id + "_" + str(j) + "_output_updated"
                #输入组件输入位置的output_updated序列
                output_bits_updated_list.append(output_bit_updated_name)
            input_bits_list = []
            for k in range(starting_bit_position, starting_bit_position + len(component.input_bit_positions[i])):
                input_bit_name = component.id + "_" + str(k) + "_input"
                input_bits_list.append(input_bit_name)
            starting_bit_position += len(component.input_bit_positions[i]) #flag表示output_bits_updated_list的值，与input_bits_list的值都存在等价关系
            flag = is_output_bits_updated_equivalent_to_input_bits(output_bits_updated_list, input_bits_list, all_equivalent_bits)
            # print("flag:",flag)
            # print(all_output_bits_available(original_input_component, available_bits))
            if all_output_bits_available(original_input_component, available_bits) and flag:
                #输入组件的所有输出output_updated_bit都是可用的，并且输入组件的output_updated序列和原组件的输入序列是存在等价关系的
                input_id_links.append(component.input_id_links[i])
                input_bit_positions.append(component.input_bit_positions[i])
            else:
                # select component for which the connected components have all their inputs available
                link = component.input_id_links[i]  #original_input_component的id
                original_input_bit_positions_of_link = component.input_bit_positions[i]
                available_output_components = get_available_output_components(original_input_component, available_bits, self)
                link_bit_names = []
                for l in range(original_input_component.output_bit_size):
                    link_bit_name = link + "_" + str(l) + "_output"  #component输入组件的输出位
                    link_bit_names.append(link_bit_name)
                for index_available_output_component, available_output_component in enumerate(
                        available_output_components):
                    if (available_output_component.id not in component.input_id_links) and (
                            available_output_component.id != component.id):
                        # print("available_output_component.id:",available_output_component.id)
                        index_id_list = [_ for _, x in enumerate(available_output_component.input_id_links) if x == link and set(original_input_bit_positions_of_link) <= set(available_output_component.input_bit_positions[_])]
                        index_id = index_id_list[0] if index_id_list else available_output_component.input_id_links.index(link)
                        # print("index_id_list:",index_id_list)
                        # print(index_id)
                        starting_bit = 0
                        for index_list, list_bit_positions in enumerate(available_output_component.input_bit_positions):
                            if index_list == index_id:
                                break
                            if starting_bit + len(list_bit_positions) < available_output_component.output_bit_size:
                                starting_bit += len(list_bit_positions)
                        available_output_component_bit_name = available_output_component.id + "_" + str(
                            starting_bit) + "_output_updated"  #满足if条件的所有available_output_component,与link相关的输入位的起始位置
                        # print("available_output_component_bit_name:",available_output_component_bit_name)
                        # print("x:",is_bit_adjacent_to_list_of_bits(available_output_component_bit_name, link_bit_names,
                        #                                    all_equivalent_bits))
                        if is_bit_adjacent_to_list_of_bits(available_output_component_bit_name, link_bit_names,
                                                           all_equivalent_bits):
                            # if all_input_bits_available(c, available_bits):
                            input_id_links.append(available_output_component.id)
                            # get input bit positions
                            accumulator = 0 # changed
                            for j in range(len(available_output_component.input_id_links)):
                                if j == index_id:
                                    # print("set(original_input_bit_positions_of_link):",original_input_bit_positions_of_link)
                                    # print("set(available_output_component.input_bit_positions[j]):",available_output_component.input_bit_positions[j])
                                    if set(original_input_bit_positions_of_link) <= set(available_output_component.input_bit_positions[j]):
                                        accumulator += original_input_bit_positions_of_link[0] - available_output_component.input_bit_positions[j][0]
                                        # print("accumulator:",accumulator)
                                    # print(accumulator)
                                    l = [h for h in range(accumulator, accumulator + len(component.input_bit_positions[i]))]
                                    # print("l:",l)
                                    l_ordered = find_correct_order(link, original_input_bit_positions_of_link, available_output_component.id, l, available_output_component.output_bit_size, all_equivalent_bits)
                                    # print(l_ordered)
                                    input_bit_positions.append(l_ordered)
                                    break
                                else:
                                    accumulator += len(available_output_component.input_bit_positions[j]) # changed
                                    # if accumulator + len(available_output_component.input_bit_positions[j])<available_output_component.output_bit_size:
                                    #     accumulator += len(available_output_component.input_bit_positions[j]) # changed
    else:
        # print(200)
        input_id_links = [[]]
        input_bit_positions = [[]]

    # print(input_bits_list)
    # print(input_id_links)
    # print(input_bit_positions)
    if KSA==True and input_id_links==[] and input_bit_positions==[]:
        # print("x")
        input_id_links = component.input_id_links
        input_bit_positions = component.input_bit_positions
    # print(input_id_links)
    # print(input_bit_positions)

    empty_indices = [j for j, positions in enumerate(input_bit_positions) if positions == []]
    for index in sorted(empty_indices, reverse=True):   #将序列中空的值去掉
        del input_id_links[index]
        del input_bit_positions[index]

    #evaluted_component的input_id_links可能是原组件的input_id_links的一部分，也可能是link的其他输出组件

    evaluated_component = Component(component.id, component.type, Input(component.input_bit_size, input_id_links, input_bit_positions),
                                    component.output_bit_size, component.description)
    evaluated_component.__class__ = component.__class__
    setattr(evaluated_component, "round", getattr(component, "round"))
    #evaluted_component相当于原组件，在input_id_links和input_bit_positions上发生改变，但是组件相关的功能并没有发生改变，如经过同一个S盒

    id = component.id
    for i in range(evaluated_component.output_bit_size):
        output_bit_name_updated = id + "_" + str(i) + "_output_updated"
        bit = {
            "component_id": id,
            "position": i,
            "type": "output_updated"
        }
        available_bits.append(bit)
        output_bit_name = id + "_" + str(i) + "_output"
        if output_bit_name not in all_equivalent_bits.keys():
            all_equivalent_bits[output_bit_name] = []
        all_equivalent_bits[output_bit_name].append(output_bit_name_updated)
        if output_bit_name_updated not in all_equivalent_bits.keys():
            all_equivalent_bits[output_bit_name_updated] = []
        all_equivalent_bits[output_bit_name_updated].append(output_bit_name)
        for name in all_equivalent_bits[output_bit_name]:
            if name != output_bit_name_updated:
                all_equivalent_bits[output_bit_name_updated].append(name)
        #将当前组件的output_updated_bit设置为available，并且在equivalent中，将output_updated_bit和output_bit构建等价关系
    # print(evaluated_component.description)
    # print(evaluated_component.id)

    return evaluated_component


def cipher_find_component(cipher, round_number, component_id):
    rounds = cipher._rounds.round_at(round_number)._components
    return next((item for item in rounds if item.id == component_id), None)

def delete_orphan_links(cipher, round_number):
    """
    Delete orphans elements from input_id_link
    INPUT:
    - ``cipher`` -- dictionary with a graph representation
    - ``round_number`` -- round index
    """
    new_components = []
    cipher_round = deepcopy(cipher._rounds.round_at(round_number)._components)
    for component in cipher_round:
        for input_id_link in component.input_id_links:
            if cipher_find_component(cipher, round_number, input_id_link) == None:
                idx = component.input_id_links.index(input_id_link)
                component.input_id_links[idx] = ''
        new_components.append(component)
    return new_components

def topological_sort(round_list):
    """
    Perform topological sort on round components.
    INPUT:
    - ``round_list`` -- list of components
    """
    pending = [(component.id, set(component.input_id_links)) for component in round_list]
    emitted = ['']
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            component_id, input_id_links = entry
            input_id_links.difference_update(emitted)
            if input_id_links:
                next_pending.append(entry)
            else:
                yield component_id
                emitted.append(component_id)
                next_emitted.append(component_id)
        if not next_emitted:
            raise ValueError("cyclic or missing dependancy detected: %r" % (next_pending,))
        pending = next_pending
        emitted = next_emitted

def sort_cipher_graph(cipher):
    """
    Sorts the cipher graph in a way that
    each component input is defined before the current component.

    INPUT:
    - ``cipher`` -- graph representation of a cipher as a python dictionary

    EXAMPLE::
        sage: from claasp.ciphers.block_ciphers.identity_block_cipher import IdentityBlockCipher
        sage: from claasp.cipher_modules.inverse_cipher import sort_cipher_graph
        sage: identity = IdentityBlockCipher()
        sage: sort_cipher_graph(identity)
        identity_block_cipher_p32_k32_o32_r1
    """

    k = 0
    for _ in range(cipher.number_of_rounds):
        round_components = delete_orphan_links(cipher, k)
        ordered_ids = list(topological_sort(round_components))
        id_dict = {d.id: d for d in cipher._rounds.round_at(k)._components}
        cipher._rounds.round_at(k)._components = [id_dict[i] for i in ordered_ids]
        k = k + 1

    return cipher

def remove_components_from_rounds(cipher, start_round, end_round, keep_key_schedule):
    list_of_rounds = cipher.rounds_as_list[:start_round] + cipher.rounds_as_list[end_round + 1:]
    key_schedule_component_ids = get_key_schedule_component_ids(cipher)
    key_schedule_components = [cipher.get_component_from_id(id) for id in key_schedule_component_ids if INPUT_KEY not in id]

    if not keep_key_schedule:
        for current_round in cipher.rounds_as_list:
            for key_component in set(key_schedule_components).intersection(current_round.components):
                cipher.rounds.remove_round_component(current_round.id, key_component)

    removed_component_ids = []
    intermediate_outputs = {}
    for current_round in list_of_rounds:
        for component in set(current_round.components) - set(key_schedule_components):
            if component.type == INTERMEDIATE_OUTPUT and component.description == ['round_output']:
                intermediate_outputs[current_round.id] = component
            cipher.rounds.remove_round_component(current_round.id, component)
            removed_component_ids.append(component.id)

    return removed_component_ids, intermediate_outputs

def get_relative_position(target_link, target_bit_positions, intermediate_output):
    if target_link == intermediate_output.id:
        return target_bit_positions

    intermediate_output_position_links = {}
    current_bit_position = 0
    for input_id_link, input_bit_positions in zip(intermediate_output.input_id_links, intermediate_output.input_bit_positions):
        for i in input_bit_positions:
            intermediate_output_position_links[(input_id_link, i)] = current_bit_position
            current_bit_position += 1

    return [intermediate_output_position_links[(target_link, bit)] for bit in target_bit_positions if (target_link, bit) in intermediate_output_position_links]

def get_most_recent_intermediate_output(target_link, intermediate_outputs):
    for index in sorted(intermediate_outputs, reverse=True):
        if target_link in intermediate_outputs[index].input_id_links or target_link == intermediate_outputs[index].id:
            return intermediate_outputs[index]

def update_input_links_from_rounds(cipher_rounds, removed_components, intermediate_outputs):
    for round in cipher_rounds:
        for component in round.components:
            for i, link in enumerate(component.input_id_links):
                if link in removed_components:
                    intermediate_output = get_most_recent_intermediate_output(link, intermediate_outputs)
                    component.input_id_links[i] = f'{intermediate_output.id}'
                    component.input_bit_positions[i] = get_relative_position(link, component.input_bit_positions[i],
                                                                             intermediate_output)
