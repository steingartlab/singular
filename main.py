from singular.implement import load

        
def main():
    """For illustration purposes"""
    
    dummy_ids = {
        'ivium': '20210621_c10x3_c3_acoustics60',
        'squidstat': '1_AP_Si_Formation_EIS-Open Circuit Potential 20230623 175329',
        'biologic': 'KS_2023_05_16_cont',
        'neware': 'GM_GT_FR2_2023_05_04_1'
    }

    for cycler, dummy_id in dummy_ids.items():
        print(cycler.upper())
        echem = load(id_=dummy_id)
        print(echem.info())


if __name__ == '__main__':
    main()