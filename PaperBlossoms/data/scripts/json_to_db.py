import os
import sqlite3
import json


def connect_db(db_file):

    # Delete database file if it exists
    if os.path.exists(db_file):
        os.remove(db_file)

    # Create connection to new database file
    conn = sqlite3.connect(db_file)
    return conn


def create_tables(db_conn, table_stem, create_stmt, foreign_key = None):

    # Set names of base and user tables, respectively
    base_table = 'base_' + table_stem
    user_table = 'user_' + table_stem

    # Create tables using the same statements
    db_conn.execute(create_stmt.format(base_table))
    db_conn.execute(create_stmt.format(user_table))

    # Create view combining both tables
    if foreign_key is not None:
        db_conn.execute(
            '''CREATE VIEW {table_stem}
            AS SELECT t.*, desc.description, desc.short_desc
            FROM (
                SELECT * FROM {base_table}
                UNION ALL
                SELECT * FROM {user_table}
            ) t
            LEFT JOIN user_descriptions desc
            ON t.{foreign_key} = desc.name'''.format(
                table_stem = table_stem,
                base_table = base_table,
                user_table = user_table,
                foreign_key = foreign_key
            )
        )
    else:
        db_conn.execute(
            '''CREATE VIEW {table_stem} AS
            SELECT * FROM {base_table}
            UNION ALL
            SELECT * FROM {user_table}'''.format(
                table_stem = table_stem,
                base_table = base_table,
                user_table = user_table
            )
        )


def rings_to_db(db_conn):

    # Create rings table
    db_conn.execute(
        '''CREATE TABLE rings (
            name TEXT PRIMARY KEY,
            outstanding_quality TEXT
        )'''
    )

    # Read rings JSON
    with open('json/rings.json', encoding = 'utf8') as f:
        rings = json.load(f)

    # Write rings to rings table
    for ring in rings:
        db_conn.execute(
            'INSERT INTO rings VALUES (?,?)',
            (ring['name'], ring['outstanding_quality'])
        )


def skills_to_db(db_conn):

    # Create skills table
    create_tables(
        db_conn,
        'skills',
        '''CREATE TABLE {} (
            skill_group TEXT,
            skill TEXT PRIMARY KEY
        )'''
    )

    # Read skills JSON
    with open('json/skill_groups.json', encoding = 'utf8') as f:
        skill_groups = json.load(f)

    # Write skills to skills table
    for skill_group in skill_groups:
        for skill in skill_group['skills']:
            db_conn.execute(
                'INSERT INTO base_skills VALUES (?,?)',
                (skill_group['name'], skill)
            )


def qualities_to_db(db_conn):

    # Create qualities table
    create_tables(
        db_conn,
        'qualities',
        '''CREATE TABLE {} (
            quality TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER
        )''',
        'quality'
    )

    # Read qualities JSON
    with open('json/qualities.json', encoding = 'utf8') as f:
        qualities = json.load(f)

    # Write qualities to qualities table
    for quality in qualities:
        db_conn.execute(
            'INSERT INTO base_qualities VALUES (?,?,?)',
            (
                quality['name'],
                quality['reference']['book'],
                quality['reference']['page']
            )
        )


def personal_effects_to_db(db_conn):

    # Create personal effects table
    create_tables(
        db_conn,
        'personal_effects',
        '''CREATE TABLE {} (
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            price_value INTEGER,
            price_unit TEXT,
            rarity TEXT
        )''',
        'name'
    )

    # Create personal effects qualities table
    create_tables(
        db_conn,
        'personal_effect_qualities',
        '''CREATE TABLE {} (
            personal_effect TEXT,
            quality TEXT
        )'''
    )

    # Read personal effects JSON
    with open('json/personal_effects.json', encoding = 'utf8') as f:
        personal_effects = json.load(f)

    # Write personal effects to personal effects tables
    for item in personal_effects:

        # Write personal effects to personal effects table
        db_conn.execute(
            'INSERT INTO base_personal_effects VALUES (?,?,?,?,?,?)',
            (
                item['name'],
                item['reference']['book'],
                item['reference']['page'],
                item['price']['value'] if 'price' in item else None,
                item['price']['unit'] if 'price' in item else None,
                item['rarity'] if 'rarity' in item else None
            )
        )

        # Write personal effect qualities
        if 'qualities' in item:
            db_conn.executemany(
                'INSERT INTO base_personal_effect_qualities VALUES (?,?)',
                [
                    (item['name'], quality)
                    for quality in item['qualities']
                ]
            )


def armor_to_db(db_conn):

    # Create armor table
    create_tables(
        db_conn,
        'armor',
        '''CREATE TABLE {} (
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            rarity INTEGER,
            price_value INTEGER,
            price_unit TEXT
        )''',
        'name'
    )
    # Create resistance values table
    create_tables(
        db_conn,
        'armor_resistance',
        '''CREATE TABLE {} (
            armor TEXT,
            resistance_category TEXT,
            resistance_value INTEGER
        )'''
    )
    # Create qualities table
    create_tables(
        db_conn,
        'armor_qualities',
        '''CREATE TABLE {} (
            armor TEXT,
            quality TEXT
        )'''
    )

    # Read armor JSON
    with open('json/armor.json', encoding = 'utf8') as f:
        armor = json.load(f)

    # Write armor to armor, resistance values and qualities tables
    for piece in armor:

        # Write to armor table
        db_conn.execute(
            'INSERT INTO base_armor VALUES (?,?,?,?,?,?)',
            (
                piece['name'],
                piece['reference']['book'],
                piece['reference']['page'],
                piece['rarity'],
                piece['price']['value'],
                piece['price']['unit']
            )
        )
        # Write to resistance values table
        for resistance_value in piece['resistance_values']:
            db_conn.execute(
                'INSERT INTO base_armor_resistance VALUES (?,?,?)',
                (
                    piece['name'],
                    resistance_value['category'],
                    resistance_value['value']
                )
            )
        # Write to qualities table
        for quality in piece['qualities']:
            db_conn.execute(
                'INSERT INTO base_armor_qualities VALUES (?,?)',
                (piece['name'], quality)
            )


def weapons_to_db(db_conn):

    # Create weapons table
    create_tables(
        db_conn,
        'weapons',
        '''CREATE TABLE {} (
            category TEXT,
            name TEXT,
            reference_book TEXT,
            reference_page INTEGER,
            skill TEXT,
            grip TEXT,
            range_min INTEGER,
            range_max INTEGER,
            damage INTEGER,
            deadliness INTEGER,
            rarity INTEGER,
            price_value INTEGER,
            price_unit TEXT,
            PRIMARY KEY (name, grip)
        )''',
        'name'
    )
    # Create qualities table
    create_tables(
        db_conn,
        'weapon_qualities',
        '''CREATE TABLE {} (
            weapon TEXT,
            grip TEXT,
            quality TEXT
        )'''
    )

    # Read weapons JSON
    with open('json/weapons.json', encoding = 'utf8') as f:
        weapon_categories = json.load(f)

    # Write weapons to weapons and qualities tables
    for category in weapon_categories:
        for weapon in category['entries']:
            for grip in weapon['grips']:

                # Write to weapons table
                db_conn.execute(
                    'INSERT INTO base_weapons VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (
                        category['name'],
                        weapon['name'],
                        weapon['reference']['book'],
                        weapon['reference']['page'],
                        (
                            weapon['skill']
                            if not any([
                                effect['attribute'] == 'skill'
                                for effect in grip['effects']
                            ])
                            else [
                                effect['value']
                                for effect in grip['effects']
                                if effect['attribute'] == 'skill'
                            ].pop()
                        ),
                        grip['name'],
                        (
                            weapon['range']['min']
                            if not any([
                                effect['attribute'] == 'range'
                                for effect in grip['effects']
                            ])
                            else [
                                effect['value']['min']
                                for effect in grip['effects']
                                if effect['attribute'] == 'range'
                            ].pop()
                        ),
                        (
                            weapon['range']['max']
                            if not any([
                                effect['attribute'] == 'range'
                                for effect in grip['effects']
                            ])
                            else [
                                effect['value']['max']
                                for effect in grip['effects']
                                if effect['attribute'] == 'range'
                            ].pop()
                        ),
                        (
                            weapon['damage']
                            if not any([
                                effect['attribute'] == 'damage'
                                for effect in grip['effects']
                            ])
                            else [
                                weapon['damage'] + effect['value_increase']
                                for effect in grip['effects']
                                if effect['attribute'] == 'damage'
                            ].pop()
                        ),
                        (
                            weapon['deadliness']
                            if not any([
                                effect['attribute'] == 'deadliness'
                                for effect in grip['effects']
                            ])
                            else [
                                weapon['deadliness'] + effect['value_increase']
                                for effect in grip['effects']
                                if effect['attribute'] == 'deadliness'
                            ].pop()
                        ),
                        weapon['rarity'],
                        weapon['price']['value'],
                        weapon['price']['unit']
                    )
                )

                # Write grip effect to qualities table
                if any([effect['attribute'] == 'quality' for effect in grip['effects']]):
                    db_conn.executemany(
                        'INSERT INTO base_weapon_qualities VALUES (?,?,?)',
                        [
                            (weapon['name'], grip['name'], effect['value'])
                            for effect in grip['effects']
                            if effect['attribute'] == 'quality'
                        ]
                    )

            # Write to qualities table
            db_conn.executemany(
                'INSERT INTO base_weapon_qualities VALUES (?,?,?)',
                [
                    (weapon['name'], None, quality)
                    for quality in weapon['qualities']
                ]
            )


def techniques_to_db(db_conn):

    # Create techniques table
    create_tables(
        db_conn,
        'techniques',
        '''CREATE TABLE {} (
            category TEXT,
            subcategory TEXT,
            name TEXT PRIMARY KEY,
            restriction TEXT,
            reference_book TEXT,
            reference_page INTEGER,
            rank INTEGER,
            xp INTEGER
        )''',
        'name'
    )

    # Read techniques JSON
    with open('json/techniques.json', encoding = 'utf8') as f:
        technique_categories = json.load(f)

    # Write techniques to techniques table
    for category in technique_categories:
        for subcategory in category['subcategories']:
            for technique in subcategory['techniques']:
                db_conn.execute(
                    'INSERT INTO base_techniques VALUES (?,?,?,?,?,?,?,?)',
                    (
                        category['name'],
                        subcategory['name'],
                        technique['name'],
                        technique['restriction'] if 'restriction' in technique else None,
                        technique['reference']['book'],
                        technique['reference']['page'],
                        technique['rank'],
                        technique['xp']
                    )
                )


def advantages_to_db(db_conn):

    # Create advantages table
    create_tables(
        db_conn,
        'advantages_disadvantages',
        '''CREATE TABLE {} (
            category TEXT,
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            ring TEXT,
            types TEXT,
            effects TEXT
        )''',
        'name'
    )

    # Read advantages JSON
    with open('json/advantages_disadvantages.json', encoding = 'utf8') as f:
        advantage_categories = json.load(f)

    # Write advantages to advantages table
    for category in advantage_categories:
        for entry in category['entries']:
            db_conn.execute(
                'INSERT INTO base_advantages_disadvantages VALUES (?,?,?,?,?,?,?)',
                (
                    category['name'],
                    entry['name'],
                    entry['reference']['book'],
                    entry['reference']['page'],
                    entry['ring'],
                    ', '.join(entry['types']),
                    entry['effects']
                )
            )


def q8_to_db(db_conn):

    # Create question 8 table
    db_conn.execute(
        '''CREATE TABLE base_unorthodox_skills (
            skill TEXT PRIMARY KEY
        )'''
    )

    # Read question 8 JSON
    with open('json/question_8.json', encoding = 'utf8') as f:
        question_8 = json.load(f)

    # Write question 8 to table
    db_conn.executemany(
        'INSERT INTO base_unorthodox_skills VALUES (?)',
        [(skill,) for skill in question_8[1]['outcome']['values']]
    )


def clans_to_db(db_conn):

    # Create clans, families, family rings and family skills tables
    create_tables(
        db_conn,
        'clans',
        '''CREATE TABLE {} (
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            type TEXT,
            ring TEXT,
            skill TEXT,
            status INTEGER
        )''',
        'name'
    )
    create_tables(
        db_conn,
        'families',
        '''CREATE TABLE {} (
            clan TEXT,
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            glory TEXT,
            wealth TEXT
        )''',
        'name'
    )
    create_tables(
        db_conn,
        'family_rings',
        '''CREATE TABLE {} (
            family TEXT,
            ring TEXT
        )'''
    )
    create_tables(
        db_conn,
        'family_skills',
        '''CREATE TABLE {} (
            family TEXT,
            skill TEXT
        )'''
    )

    # Read clans JSON
    with open('json/clans.json', encoding = 'utf8') as f:
        clans = json.load(f)

    # Write to tables
    for clan in clans:

        # Write to clans table
        db_conn.execute(
            'INSERT INTO base_clans VALUES (?,?,?,?,?,?,?)',
            (
                clan['name'],
                clan['reference']['book'],
                clan['reference']['page'],
                clan['type'],
                clan['ring_increase'],
                clan['skill_increase'],
                clan['status']
            )
        )

        for family in clan['families']:

            # Write to families table
            db_conn.execute(
                'INSERT INTO base_families VALUES (?,?,?,?,?,?)',
                (
                    clan['name'],
                    family['name'],
                    family['reference']['book'],
                    family['reference']['page'],
                    family['glory'],
                    family['wealth']
                )
            )

            # Write to family rings table
            db_conn.executemany(
                'INSERT INTO base_family_rings VALUES (?,?)',
                [
                    (family['name'], ring)
                    for ring in family['ring_increase']
                ]
            )

            # Write to family skills table
            db_conn.executemany(
                'INSERT INTO base_family_skills VALUES (?,?)',
                [
                    (family['name'], skill)
                    for skill in family['skill_increase']
                ]
            )


def heritage_to_db(db_conn):

    # Create heritage, heritage modifier, heritage effects table
    db_conn.execute(
        '''CREATE TABLE samurai_heritage (
            source TEXT,
            roll_min INTEGER,
            roll_max INTEGER,
            ancestor TEXT PRIMARY KEY,
            modifier_glory INTEGER,
            modifier_honor INTEGER,
            modifier_status INTEGER,
            effect_type TEXT,
            effect_instructions TEXT
        )'''
    )
    db_conn.execute(
        '''CREATE TABLE heritage_effects (
            ancestor TEXT,
            roll_min INTEGER,
            roll_max INTEGER,
            outcome TEXT
        )'''
    )

    # Read samurai heritage from JSON
    with open('json/samurai_heritage.json', encoding = 'utf8') as f:
        samurai_heritage = json.load(f)

    # Write to heritage tables
    for ancestor in samurai_heritage:

        # Write to samurai heritage table
        db_conn.execute(
            'INSERT INTO samurai_heritage VALUES (?,?,?,?,?,?,?,?,?)',
            (
                ancestor['source'],
                ancestor['roll']['min'],
                ancestor['roll']['max'],
                ancestor['result'],
                ancestor['modifiers']['glory'],
                ancestor['modifiers']['honor'],
                ancestor['modifiers']['status'],
                ancestor['other_effects']['type'],
                ancestor['other_effects']['instructions']
            )
        )

        # Write to heritage effects table
        if 'outcomes' in ancestor['other_effects']:
            db_conn.executemany(
                'INSERT INTO heritage_effects VALUES (?,?,?,?)',
                [
                    (
                        ancestor['result'],
                        effect['roll']['min'] if 'roll' in effect else None,
                        effect['roll']['max'] if 'roll' in effect else None,
                        effect['outcome']
                    )
                    for effect in ancestor['other_effects']['outcomes']
                ]
            )


def schools_to_db(db_conn):

    # Create school tables
    create_tables(
        db_conn,
        'schools',
        '''CREATE TABLE {} (
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            role TEXT,
            clan TEXT,
            starting_skills_size INTEGER,
            honor INTEGER,
            advantage_disadvantage TEXT,
            school_ability_name TEXT,
            mastery_ability_name TEXT
        )'''
    )
    create_tables(
        db_conn,
        'school_rings',
        '''CREATE TABLE {} (
            school TEXT,
            ring TEXT
        )'''
    )
    create_tables(
        db_conn,
        'school_starting_skills',
        '''CREATE TABLE {} (
            school TEXT,
            skill TEXT
        )'''
    )
    create_tables(
        db_conn,
        'school_techniques_available',
        '''CREATE TABLE {} (
            school TEXT,
            technique TEXT
        )'''
    )
    create_tables(
        db_conn,
        'school_starting_techniques',
        '''CREATE TABLE {} (
            school TEXT,
            set_id INTEGER,
            set_size INTEGER,
            technique TEXT
        )'''
    )
    create_tables(
        db_conn,
        'school_starting_outfit',
        '''CREATE TABLE {} (
            school TEXT,
            set_id INTEGER,
            set_size INTEGER,
            equipment TEXT
        )'''
    )
    create_tables(
        db_conn,
        'curriculum',
        '''CREATE TABLE {} (
            school TEXT,
            rank INTEGER,
            advance TEXT,
            type TEXT,
            special_access INTEGER
        )'''
    )

    # Create schools view custom because of multiple description fields
    db_conn.execute('DROP VIEW schools')
    db_conn.execute(
        '''CREATE VIEW schools AS
        SELECT
            t.*,
            desc.description,
            desc.short_desc,
            school_ability_desc.description AS school_ability_description,
            school_ability_desc.short_desc AS school_ability_short_desc,
            mastery_ability_desc.description AS mastery_ability_description,
            mastery_ability_desc.short_desc AS mastery_ability_short_desc
        FROM (
            SELECT * FROM base_schools
            UNION ALL
            SELECT * FROM user_schools
        ) t
        LEFT JOIN user_descriptions desc
            ON t.name = desc.name
        LEFT JOIN user_descriptions school_ability_desc
            ON t.school_ability_name = school_ability_desc.name
        LEFT JOIN user_descriptions mastery_ability_desc
            ON t.mastery_ability_name = mastery_ability_desc.name'''
    )

    # Read schools JSON
    with open('json/schools.json', encoding = 'utf8') as f:
        schools = json.load(f)

    # Write to schools tables
    for school in schools:

        # Write to schools table
        db_conn.execute(
            'INSERT INTO base_schools VALUES (?,?,?,?,?,?,?,?,?,?)',
            (
                school['name'],
                school['reference']['book'],
                school['reference']['page'],
                ', '.join(school['role']),
                school['clan'] if 'clan' in school else None,
                school['starting_skills']['size'],
                school['honor'],
                school['advantage_disadvantage'] if 'advantage_disadvantage' in school else None,
                school['school_ability'],
                school['mastery_ability'],
            )
        )

        # Write to school rings table
        db_conn.executemany(
            'INSERT INTO base_school_rings VALUES (?,?)',
            [
                (school['name'], ring)
                for ring in school['ring_increase']
            ]
        )

        # Write to school starting skill table
        db_conn.executemany(
            'INSERT INTO base_school_starting_skills VALUES (?,?)',
            [
                (school['name'], skill)
                for skill in school['starting_skills']['set']
            ]
        )

        # Write to school techniques available table
        db_conn.executemany(
            'INSERT INTO base_school_techniques_available VALUES (?,?)',
            [
                (school['name'], technique)
                for technique in school['techniques_available']
            ]
        )

        # Write to school starting techniques table
        for technique_set_id, technique_set in enumerate(school['starting_techniques']):
            db_conn.executemany(
                'INSERT INTO base_school_starting_techniques VALUES (?,?,?,?)',
                [
                    (
                        school['name'],
                        technique_set_id,
                        technique_set['size'],
                        technique
                    )
                    for technique in technique_set['set']
                ]
            )

        # Write to schools starting outfit table
        for equipment_set_id, equipment_set in enumerate(school['starting_outfit']):
            db_conn.executemany(
                'INSERT INTO base_school_starting_outfit VALUES (?,?,?,?)',
                [
                    (
                        school['name'],
                        equipment_set_id,
                        equipment_set['size'],
                        piece
                    )
                    for piece in equipment_set['set']
                ]
            )

        # Write to curriculum table
        db_conn.executemany(
            'INSERT INTO base_curriculum VALUES (?,?,?,?,?)',
            [
                (
                    school['name'],
                    advancement['rank'],
                    advancement['advance'],
                    advancement['type'],
                    int(advancement['special_access'])
                )
                for advancement in school['curriculum']
            ]
        )


def titles_to_db(db_conn):

    # Create titles table
    create_tables(
        db_conn,
        'titles',
        '''CREATE TABLE {} (
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            base_status_award INTEGER,
            status_award_constraint_type TEXT,
            status_award_constraint_value INTEGER,
            status_award_constraint_min INTEGER,
            status_award_constraint_max INTEGER,
            xp_to_completion INTEGER,
            title_ability_name TEXT
        )'''
    )

    # Create advancement table for titles
    create_tables(
        db_conn,
        'title_advancements',
        '''CREATE TABLE {} (
            title TEXT,
            rank INTEGER,
            name TEXT,
            type TEXT,
            special_access INTEGER
        )'''
    )

    # Create titles view custom because of multiple description fields
    db_conn.execute('DROP VIEW titles')
    db_conn.execute(
        '''CREATE VIEW titles AS
        SELECT
            t.*,
            desc.description,
            desc.short_desc,
            title_ability_desc.description AS title_ability_description,
            title_ability_desc.short_desc AS title_ability_short_desc
        FROM (
            SELECT * FROM base_titles
            UNION ALL
            SELECT * FROM user_titles
        ) t
        LEFT JOIN user_descriptions desc
            ON t.name = desc.name
        LEFT JOIN user_descriptions title_ability_desc
            ON t.title_ability_name = title_ability_desc.name'''
    )

    # Read titles from JSON
    with open('json/titles.json', encoding = 'utf8') as f:
        titles = json.load(f)

    # Write to titles tables
    for title in titles:

        # Write to titles table
        db_conn.execute(
            'INSERT INTO base_titles VALUES (?,?,?,?,?,?,?,?,?,?)',
            (
                title['name'],
                title['reference']['book'],
                title['reference']['page'],
                title['status_award']['base_award'],
                title['status_award']['constraint']['type'] if 'constraint' in title['status_award'] and 'value' in title['status_award']['constraint'] else None,
                title['status_award']['constraint']['value'] if 'constraint' in title['status_award'] and 'value' in title['status_award']['constraint'] else None,
                title['status_award']['constraint']['range'][0] if 'constraint' in title['status_award'] and 'range' in title['status_award']['constraint'] else None,
                title['status_award']['constraint']['range'][1] if 'constraint' in title['status_award'] and 'range' in title['status_award']['constraint'] else None,
                title['xp_to_completion'],
                title['title_ability'],
            )
        )

        # Write to title advancement table
        db_conn.executemany(
            'INSERT INTO base_title_advancements VALUES (?,?,?,?,?)',
            [
                (
                    title['name'],
                    advancement['rank'] if 'rank' in advancement else None,
                    advancement['name'],
                    advancement['type'],
                    advancement['special_access']
                )
                for advancement in title['advancements']
            ]
        )


def patterns_to_db(db_conn):
    
    # Create item patterns table
    create_tables(
        db_conn,
        'item_patterns',
        '''CREATE TABLE {} (
            name TEXT PRIMARY KEY,
            reference_book TEXT,
            reference_page INTEGER,
            xp_cost INTEGER,
            rarity_modifier INTEGER
        )''',
        'name'
    )

    # Read item patterns from JSON
    with open('json/item_patterns.json', encoding = 'utf8') as f:
        item_patterns = json.load(f)
    
    # Write item patterns to item pattern table
    for pattern in item_patterns:
        db_conn.execute(
            'INSERT INTO base_item_patterns VALUES (?,?,?,?,?)',
            (
                pattern['name'],
                pattern['reference']['book'],
                pattern['reference']['page'],
                pattern['xp_cost'],
                pattern['rarity_modifier']
            )
        )


def desc_to_db(db_conn):
    db_conn.execute(
        '''CREATE TABLE user_descriptions (
            name TEXT PRIMARY KEY,
            description TEXT,
            short_desc TEXT
        )'''
    )


def main():

    # Change working directory to data folder
    os.chdir(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__)
            ))
    )

    # Open connection
    db_conn = connect_db('paperblossoms.db')

    # Descriptions
    desc_to_db(db_conn)

    # Easy tables
    rings_to_db(db_conn)
    skills_to_db(db_conn)
    techniques_to_db(db_conn)
    advantages_to_db(db_conn)
    q8_to_db(db_conn)
    titles_to_db(db_conn)
    patterns_to_db(db_conn)

    # Equipment
    qualities_to_db(db_conn)
    personal_effects_to_db(db_conn)
    armor_to_db(db_conn)
    weapons_to_db(db_conn)

    # The big guns
    clans_to_db(db_conn)
    heritage_to_db(db_conn)
    schools_to_db(db_conn)

    # Commit and close connection
    db_conn.commit()
    db_conn.close()


if __name__ == '__main__':
    main()
