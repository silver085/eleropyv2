def map_byte_to_address(address):
    return '{:02X}{:02X}{:02X}'.format(address[0], address[1], address[2])


def map_to_byte_address(address):
    result = []
    current_byte = ""
    current_count = 1
    for i in range(len(address)):

        current_byte = current_byte + address[i]
        if current_count < 2:
            current_count += 1
        else:
            current_count = 1
            result.append(int(current_byte, 16))
            current_byte = ""
    return result


def map_to_byte_address_wchannel(address, channel=1):
    mapped_obj = map_to_byte_address(address)
    mapped_obj.append(channel)
    return mapped_obj


def map_3bytes_addresses(addresses):
    a_list = []
    for address in addresses:
        if len(address) > 1:
            a_list.append(map_byte_to_address(address))

    return a_list


def map_from_str(address):
    return [int(address[i:i+2], 16) for i in range(0, len(address), 2)]
