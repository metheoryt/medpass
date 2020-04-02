# Generated by Django 3.0.4 on 2020-04-02 09:21

from django.db import migrations


def add_all_permissions(apps, schema_editor):
    from django.contrib.auth.management import create_permissions

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None


def default_groups_and_perms(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    P = apps.get_model('auth', 'Permission')

    inspectors = Group.objects.create(name='inspectors')
    inspectors.permissions.add(P.objects.get(codename='view_checkpoint'))

    inspectors.permissions.add(P.objects.get(codename='add_checkpointpass'))
    inspectors.permissions.add(P.objects.get(codename='change_checkpointpass'))
    inspectors.permissions.add(P.objects.get(codename='view_checkpointpass'))

    inspectors.permissions.add(P.objects.get(codename='view_country'))

    inspectors.permissions.add(P.objects.get(codename='view_marker'))

    inspectors.permissions.add(P.objects.get(codename='add_person'))
    inspectors.permissions.add(P.objects.get(codename='change_person'))
    inspectors.permissions.add(P.objects.get(codename='view_person'))

    inspectors.permissions.add(P.objects.get(codename='view_region'))


def default_regions(apps, schema_editor):
    Region = apps.get_model('core', 'Region')
    Country = apps.get_model('core', 'Country')
    kz = Country.objects.get(pk=85)  # Казахстан

    for r in [
        Region(name='АКМОЛИНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-akm.dmed.kz/WebApi2.3/api/'),
        Region(name='АКТЮБИНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-akt.dmed.kz/WebApi2.3/api/'),
        Region(name='АЛМАТИНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-ala.dmed.kz/WebApi2.3/api/'),
        Region(name='АТЫРАУСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-atr.dmed.kz/WebApi2.3/api/'),
        Region(name='ЗАПАДНО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-zko.dmed.kz/WebApi2.3/api/'),
        Region(name='ЖАМБЫЛСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-zha.dmed.kz/WebApi2.3/api/'),
        Region(name='КАРАГАНДИНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-krg.dmed.kz/WebApi2.3/api/'),
        Region(name='КОСТАНАЙСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-kos.dmed.kz/WebApi2.3/api/'),
        Region(name='КЫЗЫЛОРДИНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-kzy.dmed.kz/WebApi2.3/api/'),
        Region(name='МАНГИСТАУСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-mng.dmed.kz/WebApi2.3/api/'),
        Region(name='ЮЖНО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-uko.dmed.kz/WebApi2.3/api/'),
        Region(name='ПАВЛОДАРСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-pvd.dmed.kz/WebApi2.3/api/'),
        Region(name='СЕВЕРО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-sko.dmed.kz/WebApi2.3/api/'),
        Region(name='ВОСТОЧНО-КАЗАХСТАНСКАЯ ОБЛАСТЬ', country=kz, dmed_url='https://lkp-vko.dmed.kz/WebApi2.3/api/'),
        Region(name='АЛМАТЫ', country=kz, dmed_url='https://lkp-alm.dmed.kz/WebApi2.3/api/'),
        Region(name='АСТАНА', country=kz, dmed_url='https://lkp-ast.dmed.kz/WebApi2.3/api/')
    ]:
        r.name = r.name.capitalize()
        r.save()


def default_countries(apps, schema_editor):
    Country = apps.get_model('core', 'Country')
    for id, name in (
            (6, 'Азербайджан'),
            (16, 'Армения'),
            (85, 'Казахстан'),
            (166, 'Российская федерация'),
            (1001, 'Не указано'),
            (1002, 'Питкэрн/pitcairn, острова'),
            (1003, 'Svalbard и jan mayen, острова'),
            (1004, 'Австралия'),
            (1005, 'Австрия'),
            (1006, 'Азербайджан'),
            (1007, 'Албания'),
            (1008, 'Алжир'),
            (1009, 'Американское самоа'),
            (1010, 'Ангилья/anguilla'),
            (1011, 'Ангола'),
            (1012, 'Андорра'),
            (1013, 'Антарктика'),
            (1014, 'Антигуа и барбуда'),
            (1015, 'Аргентина'),
            (1016, 'Армения'),
            (1017, 'Аруба'),
            (1018, 'Афганистан'),
            (1019, 'Багамы'),
            (1020, 'Бангладеш'),
            (1021, 'Барбадос'),
            (1022, 'Бахрейн'),
            (1023, 'Беларусь'),
            (1024, 'Белиз'),
            (1025, 'Бельгия'),
            (1026, 'Бенин'),
            (1027, 'Бермуда'),
            (1028, 'Болгария'),
            (1029, 'Боливия'),
            (1030, 'Босния и герцеговина'),
            (1031, 'Ботсвана'),
            (1032, 'Бразилия'),
            (1033, 'Британские территории индийского океана'),
            (1034, 'Бруней дар-эс-салам'),
            (1035, 'Буркина фасо'),
            (1036, 'Бурунди'),
            (1037, 'Бутан'),
            (1038, 'Вануату'),
            (1039, 'Ватикан'),
            (1040, 'Венгрия'),
            (1041, 'Венесуэла'),
            (1042, 'Виргинские острова (британия)'),
            (1043, 'Виргинские острова (сша)'),
            (1044, 'Восточный тимор'),
            (1045, 'Вьетнам'),
            (1046, 'Габон'),
            (1047, 'Гаити'),
            (1048, 'Гайана'),
            (1049, 'Гамбия'),
            (1050, 'Гана'),
            (1051, 'Гваделупа'),
            (1052, 'Гватемала'),
            (1053, 'Гвинея'),
            (1054, 'Гвинея-бисау'),
            (1055, 'Германия'),
            (1056, 'Гибралтар'),
            (1057, 'Гонг-конг'),
            (1058, 'Гондурас'),
            (1059, 'Гренада'),
            (1060, 'Гренландия'),
            (1061, 'Греция'),
            (1062, 'Грузия'),
            (1063, 'Гуам'),
            (1064, 'Дания'),
            (1065, 'Джибути'),
            (1066, 'Доминика'),
            (1067, 'Доминиканская республика'),
            (1068, 'Египет'),
            (1069, 'Заир'),
            (1070, 'Замбия'),
            (1071, 'Западная сахара'),
            (1072, 'Зимбабве'),
            (1073, 'Израиль'),
            (1074, 'Индия'),
            (1075, 'Индонезия'),
            (1076, 'Иордания'),
            (1077, 'Ирак'),
            (1078, 'Иран (исламская республика)'),
            (1079, 'Ирландия'),
            (1080, 'Исландия'),
            (1081, 'Испания'),
            (1082, 'Италия'),
            (1083, 'Йемен'),
            (1084, 'Кабо верде'),
            (1085, 'Казахстан'),
            (1086, 'Каймановы острова'),
            (1087, 'Камбоджа'),
            (1088, 'Камерун'),
            (1089, 'Канада'),
            (1090, 'Катар'),
            (1091, 'Кения'),
            (1092, 'Кипр'),
            (1093, 'Кирибати'),
            (1094, 'Китай'),
            (1095, 'Кокосовые острова (keeling)'),
            (1096, 'Колумбия'),
            (1097, 'Коморы'),
            (1098, 'Конго'),
            (1099, 'Корея, демократическая народная республика'),
            (1100, 'Корея, республика'),
            (1101, 'Коста-рика'),
            (1102, 'Кот дивуар'),
            (1103, 'Куба'),
            (1104, 'Кувейт'),
            (1105, 'Кыргизстан'),
            (1106, 'Лаос, народная демократическая республика'),
            (1107, 'Латвия'),
            (1108, 'Лесото'),
            (1109, 'Либерия'),
            (1110, 'Ливан'),
            (1111, 'Ливийская арабская джамахирия'),
            (1112, 'Литва'),
            (1113, 'Лихтенштейн'),
            (1114, 'Люксембург'),
            (1115, 'Маврикий'),
            (1116, 'Мавритания'),
            (1117, 'Мадагаскар'),
            (1118, 'Майот/mayotte'),
            (1119, 'Макау'),
            (1120, 'Македония, бывшая югославская республика'),
            (1121, 'Малави'),
            (1122, 'Малайзия'),
            (1123, 'Мали'),
            (1124, 'Мальдивы'),
            (1125, 'Мальта'),
            (1126, 'Марокко'),
            (1127, 'Мартиника'),
            (1128, 'Маршалловы острова'),
            (1129, 'Мексика'),
            (1130, 'Микронезия, федерация штатов'),
            (1131, 'Мозамбик'),
            (1132, 'Молдова, республика'),
            (1133, 'Монако'),
            (1134, 'Монголия'),
            (1135, 'Монтсеррат'),
            (1136, 'Намибия'),
            (1137, 'Науру'),
            (1138, 'Непал'),
            (1139, 'Нигер'),
            (1140, 'Нигерия'),
            (1141, 'Нидерландские антилы'),
            (1142, 'Нидерланды'),
            (1143, 'Никарагуа'),
            (1144, 'Ниуэ/niue'),
            (1145, 'Новая зеландия'),
            (1146, 'Новая каледония'),
            (1147, 'Норвегия'),
            (1148, 'Норфолк, остров'),
            (1149, 'Ньянмар (бирма)'),
            (1150, 'Объединённые арабские эмираты'),
            (1151, 'Оман'),
            (1152, 'Острова heard и mc donald'),
            (1153, 'Острова бувэ/bouvet'),
            (1154, 'Острова кука'),
            (1155, 'Пакистан'),
            (1156, 'Палау'),
            (1157, 'Панама'),
            (1158, 'Папуа новая гвинея'),
            (1159, 'Парагвай'),
            (1160, 'Перу'),
            (1161, 'Польша'),
            (1162, 'Португалия'),
            (1163, 'Пуэрто рико'),
            (1164, 'Реюньон'),
            (1165, 'Рождества/christmas, острова'),
            (1166, 'Россия'),
            (1167, 'Руанда'),
            (1168, 'Румыния'),
            (1169, 'Самоа'),
            (1170, 'Сан марино'),
            (1171, 'Сан томе и принсипе'),
            (1172, 'Саудовская аравия'),
            (1173, 'Св. Елена'),
            (1174, 'Свазиленд'),
            (1175, 'Северные марианские острова'),
            (1176, 'Сейшелы'),
            (1177, 'Сенегал'),
            (1178, 'Сент пьер и миклон/miquelon'),
            (1179, 'Сент-винсент и гренадины'),
            (1180, 'Сент-Китс и Невис'),
            (1181, 'Сент-люсия'),
            (1182, 'Сингапур'),
            (1183, 'Сирийская арабская республика'),
            (1184, 'Словакия (словацкая республика)'),
            (1185, 'Словения'),
            (1186, 'Соединённое королевство (великобритания)'),
            (1187, 'Соединённые штаты'),
            (1188, 'Соединённые штаты без островов'),
            (1189, 'Соломоновы острова'),
            (1190, 'Сомали'),
            (1191, 'Судан'),
            (1192, 'Суринам'),
            (1193, 'Сьерра леоне'),
            (1194, 'Таджикистан'),
            (1195, 'Таиланд'),
            (1196, 'Тайвань'),
            (1197, 'Танзания, объединённая республика'),
            (1198, 'Теркс и кайкос/turks и caicos, острова'),
            (1199, 'Того'),
            (1200, 'Токелау'),
            (1201, 'Тонга'),
            (1202, 'Тринидад и тобаго'),
            (1203, 'Тувалу'),
            (1204, 'Тунис'),
            (1205, 'Туркменистан'),
            (1206, 'Турция'),
            (1207, 'Уганда'),
            (1208, 'Узбекистан'),
            (1209, 'Украина'),
            (1210, 'Уолис/wallis и футурна/futuna, острова'),
            (1211, 'Уругвай'),
            (1212, 'Фарерские/faroe о-ва'),
            (1213, 'Фиджи'),
            (1214, 'Филиппины'),
            (1215, 'Финляндия'),
            (1216, 'Фольклендские (мальвинские) острова'),
            (1217, 'Франция'),
            (1218, 'Франция, метрополия'),
            (1219, 'Французская гвиана'),
            (1220, 'Французская полинезия'),
            (1221, 'Французские южные территории'),
            (1222, 'Хорватия (местное название: hrvatska)'),
            (1223, 'Центрально-африканская республика'),
            (1224, 'Чад'),
            (1225, 'Чешская республика'),
            (1226, 'Чили'),
            (1227, 'Швейцария'),
            (1228, 'Швеция'),
            (1229, 'Шри ланка'),
            (1230, 'Эквадор'),
            (1231, 'Экваториальная гвинея'),
            (1232, 'Эль сальвадор'),
            (1233, 'Эритрея'),
            (1234, 'Эстония'),
            (1235, 'Эфиопия'),
            (1236, 'Югославия'),
            (1237, 'Южная африка'),
            (1238, 'Южная джорджия и южные сэндвичевы острова'),
            (1239, 'Ямайка'),
            (1240, 'Япония'),
            (1241, 'Антильские острова'),
            (1242, 'Джонстона, остров'),
            (1243, 'Канала, острова'),
            (1244, 'Мен, остров'),
            (1245, 'Мидуэй'),
            (1246, 'Мьянма'),
            (1247, 'Палестина'),
            (1248, 'Свальбарда, остров'),
            (1249, 'Тихоокеанские острова'),
            (1250, 'Уэйк'),
            (1251, 'Лицо без гражданства'),
            (1252, 'Черногория'),
            (1253, 'Сербия'),
            (1254, 'Аландские острова'),
            (1255, 'Бонэйр, Синт-Эстатиус и Саба'),
            (1256, 'Гернси'),
            (1257, 'Джерси'),
            (1258, 'Кюрасао'),
            (1259, 'Сен-Мартен'),
            (1260, 'Синт-Мартен (нидерландская часть)'),
            (1261, 'Сен-Бартелеми'),
            (1262, 'Китайская Республика'),
            (1263, 'Южный Судан'),
            (1264, 'Заграница'),
            (100000000000001, 'Сербия'),
            (100000000000002, 'Сектор газа'),
            (100000000000003, 'Заграница')
    ):
        Country.objects.create(id=id, name=name)


def default_markers(apps, schema_editor):
    Marker = apps.get_model('core', 'Marker')
    for id, name in (
        (52, 'КВИ: прибывшие из стран 1Б'),
        (53, 'КВИ: прибывшие из стран 2'),
        (54, 'КВИ: прибывшие из стран 3'),
        (55, 'КВИ: близкие контакты'),
        (56, 'КВИ: потенциальные контакты'),
        (57, 'КВИ: прибывшие из стран 1А'),
        (58, 'КВИ: настороженность')
    ):
        Marker.objects.create(id=id, name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_all_permissions),
        migrations.RunPython(default_countries),
        migrations.RunPython(default_regions),
        migrations.RunPython(default_groups_and_perms),
        migrations.RunPython(default_markers),
    ]
