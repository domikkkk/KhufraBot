import requests
import random
import re
import json
from login import LOGIN, PASSWORD, BEARER, BEARER2


blackbox_tokens = [
    'JVqc1PkrbpPF9zyxI5ICZ4y-BFe4Kov1WtA_ZJbI7R9ih7nrYM5BsRZ54kixFnqf0QMoWp3C9CZt0jWgDzRmmL3vMleJuxJ76U28M6bL_S9UhsnuIFKYAXPYPq0lSnyu0wVIbZ_R9ihaf7H0JEl7vvIXSYyx4xV66BVqveIUV7wqT4Gz2ApNcqTWPHCn2j5yqdwMPXDUCUGkCW6l3RRHed4XToLmSn7fRXfcFHio2Qk-cqbfQnWt4RdMhOdJr-AVRXrfE0OoDHGm1vstX4S2-R5Qgsk4pw563wQ2Zq8dgK7TBTVdnusvWH2v8jOByBRZfrDgCEmW2v8xdJnL-02uEnfmVHmr2y1mi73tH09_pNYGWb4wmf5xlsj4PKUXfN9Thsr7LFGDsymc-zCPv-QWRrYpiL0cTHWazP4jVZi97yFUiO4ihb0fT4S4HFGE6Eyu4hV3qNo_ogU-btI3bZ7SBWbIATdupgs7bqfYCTudAWPFKlu_IYbqS3uz6h6BtOkfRHaozf9CZ5nL-13D-1yMwSJZvB1VhrnyKYvsIVOK602v4UJ5ruRJea_lGk6y6RpLg7obf7LmFnms4xh94hh930GkCECj2xRGdpvN_yRWmcoDNWWKvP8wYJTE6RtekMTpG17SRLkeQ3W4LJ4TeJ3PEjdpm8wyYpX3LmXLL5DD9i1hk8X7LI7zVIToGlG27CBShedNf7EVR6kPRHvhRqgLQHPUOXClB0B2qA5Eqd4QQ6YJOWuQwvQZS46z5Rd6sedMfrATdqwNbqcNQqPZDkd_uOkiWo3vJl3AJFSMwSJVi77yVrrwVozF-DBomtEylMkqXsH3WpDBIliKwidcgbPlCjx_pNYIbqHZO50CZZrL_C2S9ixcjO1OhrbvUYW27SZewSJXju8niOwjVbnxJ1eJuexNhOggWLnvH1iM8CWJviBVuhuBtdoMPmOV2P0vYZnPMZb7XML0Wo2-91yPvyFYvCKH606EuRx_4RpKfN0WTofoGkt74Uep3EB0qt4WebHhQ6fXEEJz1DVlxvgxZJa77R9EdrnsIU-GufEkVo_E_TBgmcv9IlSXvO4gg7UWTrPoSX2tD0By1jdr0QJknP8zmfowYZfNMmmiAztvpQptptY3m9EBNGXG-i2OxCdgkMctY5TK_S5ewSaKvuMVR2ye4RJLe63lGEiAsOcMPoGm2Ao8bJ7R_i5hjsD0SHmr0ANEdq7TBkd3p9UIO3TO8yVXfK7xFkh640y98GOazC-hEkW_MJX-Ysw-d-IYjweB9WibwPIkSXu-8SdXfK7xFkh6q9sAMmSJu_4jVYfeV6jgQ70KdL8Sersel9kyhvRNxCVr0yCG3BV80Emj2i9fmAFShPxVuv43kPFboBdqsvhAkNQplOAzhP1itQtVpPhFfNUcZd4rmfxougBw0ylx1PkrccDzWozYRY76Q5bYHW_HOqv4T7Mjhcn-Zcsfh-BEsOU4gvxKnOVTvjOYyDNqzTiF90eKy0OR-16T4UukG2quEUaTDXTtEkR2m80QNWeZ5lXPOKQQcZbIDkNxocb4KFCnEH7iUcg7YJLCEGSJu-scTHqqzwJEaZvLIov5L2OIu_0iVIT8MmaLvgAlV4f5b5THCDlpotAAKU6AsPdcvyqZvvA2aJjJ-SlairvgEkKI8WPILp0VOmyy4xRFc6PI-ixRg8brHU-BseMWQ3Om0wU5jb7wFUiJu_MYS4y87BpKeqoEKVuNsuQnlQp24gc8gA',
    'JVqc1PkrbpPF9zyxI5ICZ4y-BFe4Kov1WtA_ZJbI7R9ih7nrHEFzpcr8P2SWyA9010Kx1gg6X5HU-StdtB2L717VSG2f0fYoa5DC9DqjFXrgT8fsHlB1p-oPQXOYyvwhU5bG6x1glLnrLlOFtxyKtwxfhLb5XszxI1V6rO8URnjeEkl84BRLfq7fEnar40arEEd_tukbgLnwJIjsIIHnGX62Gkp7q-AUSIHkF0-Due4mietRgrfnHIG15UquE0h4nc8BJlibwPIka9pJsByBptgIUb8iUHWn1_9AjdH6H1GU1SNqtvsgUoKq6zh8odMWO22d71C0GYj2G019zwgtX4_B8SFGeKj7YNI7oBM4apreR7kegfUobJ3O8yVVyz6d0jFhhrjoWMsqX77uFzxuoMX3Ol-Rw_YqkMQnX8HxJlq-8yaK7lCEtxlKfOFEp-AQdNkPQHSnCGqj2RBIrd0QSXqr3T-jBWfM_WHDKIztHVWMwCNWi8HmGEpvoeQJO22d_2Wd_i5jxPtev_coW5TLLY7D9SyN71GD5BtQhusbUYe88FSLvO0lXL0hVIi4G06Fuh-Euh-B40aq4kV9tugYPW-hxvg7bKXXByxeodICNmaLvQAyZou9AHTmW8DlF1rOQLUaP3G02Qs9btQEN5nQB23RMmWYzwM1Z53OMJX2Joq881iOwvQnie8hU7fpS7HmHYPoSq3iFXbbEkep4hhKsOZLgLLlSKvbDTJklrvtMFWHuRxTie4gUrUYTq8QSa_kRXuw6SFai8T8L5HI_2LG9i5jxPctYJT4XJL4Lmea0go8c9Q2a8wAY5n8MmPE-ixkyf4jVYes3iFGeKoQQ3vdP6QHPG2ezzSYzv4uj_AoWJHzJ1iPyABjxPkwkckqjsX3W5PJ-Stbju8misL6W5HB-i6SxytgwvdcvSNXfK7gBTd6n9EDO3HTOJ3-ZJb8L2CZ_jFhw_pexCmN8CZbviGDvOwef7jwKYq87R2D6Ut-4hZMgLgbU4PlSXmy5BV21wdomtMGOF2PweYYW47D8Shbk8b4MWaf0gI7bZ_E9jlekMIlV7jwVYrrH0-x4hR42Q1zpAY-odU7nNIDOW_UC0Sl3RFHrA9IeNk9c6PWB2iczzBmyQIyac8FNmyf0ABjyCxghbfpDkCDtO0dT4e66iJSia7gI0h6rN4OQHOg0AMwYpbqG01ypeYZSW6h4hdIdqbdE22SxPYbTZC15xl87lLK_mLEOpv9ddtPuyKE6hyJvSyVzkKpG01ypNb7LXCi1gcsXqHG-Cpbi7DiFDlrrtMFN4q6-3DDMJjMLpftLnurEnrRFEW3CDmoHm7oLqL0JFzOH2LOP5DD9DyG2jSI2yKG81W_EEmuGnDdQITSOYLVIorsHom9Fo_D-0ic1EKl1zuH7FiR4UeL3E2czkKS5yygC2KoAlWgC1XDHXTnWK8pe74KdKgfd-FZshN89DiGyRdZovlt5i-Y2VGfCWyh71myKne7EIfVGYD3HE6ApdcaP3Gj8F_ZQq4ae6DSGE17q9ACMlqxGojsW9JFapzMGm6TxfUmVoS02QxOc6XVLJUDOW2SxQcsXo4GPHCVyAovYZEDeZ7REkNzrNoKM1iKugFmyTSjyPpAcqLTAzNklMXqHEyS-23SOKcfRHa87R5Pfa3SBDZbjdD1J1mLu-0gTX2w3Q9Dl8j6H1KTxvYbTo_E9CJSgrIMMWOVuuwvnRJ-6g9EiA',
    'JVqc1PkrbpPF9zyxI5ICZ4y-BFe4Kov1WtA_ZJbI7R9iyCmVCG2SxAcsXpDSPqcVgKXXCS5go8j6LIPsWr4tpBc8bqDF9zpfkcMGbuBPvCFGeKrPAURpm80Ug_JZxSpPgbH6aMv5HlCCp9kcVHmr7iJHebzhE0WtH0yU5gs9gOhaf7H0Wcf0SZzB8zabCS5gkrfpLFGDtRtPhrkdUYi76xxPs-ggg-hNhLzzJli99i1hxSldviRWu_NXh7joHVGFviFUjMD2K2PGKI6_9CRZvvIih-tQhbXaDD5jldj9L2GoF4btWb7jFUWO_F-NsuQUPH3KDjdcjtESYKfzOF2Pv-codbneEFN4qtosjfFWxTNYiroMZIm76yBYiK3fD2LHOaIHep_RAUWuIIXoXI_TBDVajLwypQQ5mMjtH0-_MpHGJVV6rO8URna67TFik7zhE0VqnN8ENmjML1-W-FuS9CVblMwDZJn7Mpb8NGyk1ws8bM4AY5fIKozxV4u88yZblPhbj_EmW5P1WJHyU7UXS4HmHE5-30R4nc8BJlibwPIkiMEiiL8ggbIWRnbcDj5w1Q0_eKkPdKjhQ3yv4xd9s-wjV43D9iuQ9VaLviNavyCD6B5WueoagLPjFXjbFEd62wAyZIm7_i9omsrvIWSVxfkpToDD9SlOgMM3qR6DqNodkQN43QI0d5zOADGXx_pck8owlPUoW5LG-CpgkfNYuelNf7YbUYW36kyy5BZ6rA50qeBGqw1wpdg5ntUKbKXbDXOpDkN1qAtuntD1J1l-sPMYSnyxEkKnDT912z943kR0reMZUYrwVbYXe6sPQ3ziRHyx5hdPgbMYea8RRKYLQnbXBzlwqd1ActM0ZZX6W7_wJFW74BJEaZveAzVnnf5jxfsvYJL0Jlq8HVS4HEyEuu8ih-keTn-27x9Rh73tH1OMxf4vZsf9MWGRwvktk8wtkcgtZsgtk8oCY8UrXYK05gs9gKXXCT6j2hJFdq7gFE2x5Uuv4RpNfd4PQHbYDkB4ruESeLHqT7XuHlSM7yeNvyRXi8T4KFuOvvEpYpnSCGrOB2iY-luAsuQJO36v4RVDc6faDkV6rOMYSX-v5ho_cbTZCz2g0jNr0AVmmsosXY_zVIjuH4G5HFC2F01-tOpPhr8gWIzCJ4rD81S47h5RguMXSqvhRH2t5EqAsecaS3veQ6fbADJkibv-MGCRxPsza57UCzBipcr8LmCQwvUiUoWy5Bhsnc_0J2ibzfIlZpfO_DVqn_keUIKn2RxBc6UbTsY3nQF54kev4hhOg-pNr-UZgPRooAVy0zhdj8HmGFuQwfkeUJO46hxNfaLUBitdoMX3KY7USKDvIVXGKluxHnG1IYnrQpgJW673cb0SeuQtl-EvkddDds8WYKHrZJXMFWrZTqMOdaf2TLfsULoUSq_hFYDXK1uP9T1u0zd63USU6zWa_ECaE23FLWKy4lGD3DSc4zVnnABWwTmsD3iwI23nHJLkXo_HG4T3YasAVqn_VMQYfeo8tBdqqyNx2z5zwSuE_Emd6h1rr_wvVIa43Q9Sd6nbKJcReuZSs9gKUIWz4wg6apLpUsAkkwp9otQEUqbL_S1ejrzsEUSGq90NZM07caXK_T9klsY-dKjR9ihYmQl55UqhBmizHJC15y1ilcz6LWOIuuoSXaX5RpK36SxRg7MfiPNYfa_fJovuWcjxFkh4uyOVBHHW-y1zpNUGNGSSwvAgRXen-lvBIpT9IlSazwI5Z5rQ9SdZfrDzGEp8rt4QQ3Cg0wAyZrrrHUJ1tukbQHO05RxKeqraNFmLveIUV8U6phI3bLA',
    'JVqc1PkrbpPF9zyxI5ICZ4y-BFe4Kov1WtA_ZJbI7R9iyCmVCG2SxAcsXpDSPqcVgKXXCS5go8j6LIPsWr4tpBc8bqDF9zpfkcMGbuBPvCFGeKrPAURpm80Ug_JZxSpPgbH6aMv5HlCCp9kcVHmr7iJHebzhE0WtH0yU5gs9b5TGCS5gkvgsY5b6LmWYyPkskMX9YMUqYZnQAzWa0wo-ogY6mwEzmNA0ZJXF-i5im_4xaZ3TCECjBWuc0QE2m8__ZMgtYpK36RtAcrXaDD6F9GPKNpvA8iJr2Txqj8HxGVqn6xQ5a67vPYTQFTpsnMQFUpa77TBVh7cJas4zohA1Z5fpQWaYyP01ZYq87D-kFn_kV3yu3iKL_WLFOWyw4RI3aZkPguEWdaXK_CycD26jAjJXiczxI1OXyg4_cJm-8CJHebzhE0WpDDxz1Thv0QI4cangQXbYD3PZEUmBtOgZSavdQHSlB2nONGiZ0AM4cdU4bM4DOHDSNW7PMJL0KF7D-StbvCFVeqzeAzV4nc8BZZ7_ZZz9Xo_zI1O56xtNsuocVYbsUYW-IFmMwPRakMkANGqg0wht0jNomwA3nP1gxfszlsf3XZDA8lW48SRXuN0PQWaY2wxFd6fM_kFyotYGK12g0gYrXaAUhvtghbf6buBVut8RVHmr3Q50pNc5cKcNcdIFOG-j1Qc9btA1lsYqXJP4LmKUxymPwfNXietRhr0jiOpNgrUWe7LnSYK46lCG6yBShehLe63SBDZbjdD1J1mO7x-E6hxSuBxVuyFRisD2LmfNMpP0WIjsIFm_IVmOw_QsXpD1VozuIYPoH1O05BZNhrodT7ARQnLXOJzNATKYve8hRni74BJEettAotgMPW_RAzeZ-jGV-Slhl8z_ZMb7K1yTzPwuZJrK_DBpotsMQ6TaDj5un9YKcKkKbqUKQ6UKcKffQKIIOl-Rw-gaXYK05huAt-8iU4u98SqOwiiMvvcqWrvsHVO16x1Vi77vVY7HLJLL-zFpzARqnAE0aKHVBThrm84GP3av5Uer5EV11zhdj8HmGFuMvvIgUIS36yJXicD1JlyMw_ccTpG26Bp9rxBIreJDd6cJOmzQMWXL_F6W-S2T9CpbkccsY5z9NWmfBGeg0DGVy_suX8D0J4i-IVqKwSddjsT3KFi7IIS43Q9BZpjbDT1uodgQSHux6A0_gqfZCz1tn9L_L2KPwfVJeqzRBEV4rNEERXWu3AxDdtD1J1l-sPMYSnzrWsk3oA112Al_40246iOUCj-k1k-F617BIoit3xE2aKvfF090pukOQHKj0_gqXIGz9htNf-RRir8hZa_4XMc_tABEicEjVKoec6QQiO1azQBWqg5VpiCQCFfBNGzBCVe4HYjBN4zTOrEGN5_gQa_gTK0WfsgUfuZbwBNkibsBV8MNP5TZSav6P7brQa0De8cebKD3TqAWZs8ZXrDhNqMGSb0AWqH7NIX-M3_XGoLaJpP7TKXoHYnfSb0OaKvsZLIcf7QCbMU9ivRFeMZAiQInWYuw4iVKfK77auRNuSWGq90jWIa22w09Zbwlk_dm3VB1p9cleZ7QADFhj7_kF1l-sOA3oA5EeJ3QEjdpmRFHe6TJ-yts3Ey4HXTZO4bvY4i6ADVon80ANluNveUweMwZZYq8_yRWhvJbxitQgrL5XsEsm8TpG0uO9mjXRKnOAEZ3qNkHN2WVw_MYSnrNLpT1Z9D1J22i1Qw6baPI-ixRg8brHU-BseMWQ3Om0wU5jb7wFUiJvPAVSIm58R9Pf68JLmCSt-ksmg975wxBhQ',
]


def log():
    a = requests.get('https://lobby.ikariam.gameforge.com/config/configuration.js')
    gameEnvironmentId = re.search(r'"gameEnvironmentId":"(.*?)"', a.text).group(1)
    platformGameId = re.search(r'"platformGameId":"(.*?)"', a.text).group(1)

    blackbox = 'tra:' + random.choice(blackbox_tokens)

    payload = {
        "identity": LOGIN, 
        "password": PASSWORD,
        "locate": "pl_PL",
        "gfLang": "pl",
        "platformGameId": platformGameId,
        "gameEnvironmentId": gameEnvironmentId,
        "autoGameAccountCreation": False,
        "blackbox": blackbox
    }
    x = requests.post("https://gameforge.com/api/v1/auth/thin/sessions", data=payload)
    try:
        token = 'Bearer ' + x.json()['token']
        return token
    except Exception:
        return


def accounts(dump=False):
    headers = {
        "Authorization": BEARER2
    }
    y = requests.get("https://lobby.ikariam.gameforge.com/api/users/me/accounts", headers=headers).json()
    y = [x for x in y if x['server']['number'] == 1 and x['accountGroup'] == 'pl_1']
    if dump:
        with open("accounts.json", 'w') as f:
            json.dump(y, f, indent=4)
    return y


def get_info():
    headers = {
        "Authorization": BEARER2
    }
    y = requests.get("https://lobby.ikariam.gameforge.com/api/users/me", headers=headers).json()
    return y


def get_in():
    blackbox = 'tra:' + random.choice(blackbox_tokens)
    payload = {
        "blackbox": blackbox,
        "clickedButton": "account_list",
        "id": 772507,
        "server": {
            "language": "pl",
            "number": 1
        }
    }
    headers = {
        "Authorization": BEARER2
    }
    y = requests.post("https://lobby.ikariam.gameforge.com/api/users/me/loginLink", headers=headers, json=payload).json()
    return y["url"]


print(get_in())
accounts(True)
