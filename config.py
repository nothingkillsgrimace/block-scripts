#!/usr/bin/env python3
import numpy as np

filepaths={
    'past_episodes':'/data/media/block_media/Blocks/past_eps_used/',
    'save_path':'/data/media/plex_media/blocks/',
    'past_bumps':'/data/media/block_media/Blocks/past_bumps_used/',
    'shows':{
        'Nick at Nite':'/data/media/block_media/Broadcast_Shows/Nick at Nite/',
        'Adult Swim':'/data/media/block_media/Broadcast_Shows/Adult Swim/',
        'Cartoon Network':'/data/media/block_media/Broadcast_Shows/Cartoon Network/',
        'FOX':'/data/media/block_media/Broadcast_Shows/FOX/',
        'Toonami':'/data/media/block_media/Broadcast_Shows/Toonami/',
        'Boomerang':'/data/media/block_media/Broadcast_Shows/Boomerang/',
    },
    'shows_with_logos':[
        'Tom Goes To The Mayor',
    ],
    'all_commercials':{
        #'Adult Swim':'/data/media/block_media/Archived Bumps & Commercials/Commercials/AS/',
        'Nick at Nite':'/data/media/block_media/Archived Bumps & Commercials/Commercials/Nick at Nite/',
        #'FOX':'/data/media/block_media/Archived Bumps & Commercials/Commercials/FOX/',
        #'Cartoon Network':'/data/media/block_media/Archived Bumps & Commercials/Commercials/CN/'
    },
        
    
    'Adult Swim':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/AS/',
            'promos':'/data/media/block_media/Archived Bumps & Commercials/AdultSwim/Promo_Commercials/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/AdultSwim/Bumps/',
        },
        'logo':'/unraid-scripts/logo/logo_Adult Swim.png',
        'bump_logs':{
            'as_general':{
                'keyword':'General -',
                'filename':'as_general.txt'
            },
            'as_picture':{
                'keyword':'Bump -',
                'filename':'as_bumps.txt'
            },
        },
        'advisory':'/data/media/block_media/Archived Bumps & Commercials/AdultSwim/Adult Swim Advisory.mp4',
        'pool_intro':'/data/media/block_media/Archived Bumps & Commercials/AdultSwim/Bumps/Pool - Intro.mp4',
    },
    
    'Boomerang':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/CN/',
            'promos_cn':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/',
            'promos_ccf':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/CCF/Powerhouse Fridays/',
            'promos_toonami':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Promo_Commercials/TOM 2/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/Boomerang/Bumps/',
        },
        'logo':'/unraid-scripts/logo/logo_boomerang.png',
    },
    
    'Nick at Nite':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/Nick at Nite/',
            'promos':'/data/media/block_media/Archived Bumps & Commercials/Nick at Nite/Promos/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/Nick at Nite/Bumps/Jingles/',
            'schedules':'/data/media/block_media/Archived Bumps & Commercials/Nick at Nite/Bumps/',
        },
        'logo':'/unraid-scripts/logo/logo_Nick at Nite.png',
    },
    
    'Cartoon Network City':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/CN/',
            'promos_cn':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/',
            'promos_ccf':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/CCF/New Fridays/',
            'promos_toonami':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Promo_Commercials/TOM3.5/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/CN City/Bumps/',
            'schedules':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/CN City/Now Then/',
            'groovies':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Groovies/clips/',
        },
        'logo':'/unraid-scripts/logo/logo_cn.png',
        'groovies_intro':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Groovies/Groovies Intro.mp4',
        'groovies_outro':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Groovies/Groovies Outro.mp4',
        'top5_folder':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Top 5/',
        'top5_year':'2004',
    },
    
    'Cartoon Network Powerhouse':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/CN/',
            'promos_cn':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/',
            'promos_ccf':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/CCF/Powerhouse Fridays/',
            'promos_toonami':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Promo_Commercials/TOM2/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Powerhouse/',
            'schedules':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Powerhouse/up_next/',
            'station_ids':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Powerhouse/station_ids/',
            'groovies':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Groovies/clips/',
        },
        'logo':'/unraid-scripts/logo/logo_Cartoon Network.png',
        'groovies_intro':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Groovies/Groovies Intro.mp4',
        'groovies_outro':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Groovies/Groovies Outro.mp4',
        'top5_folder':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Top 5/',
        'top5_year':'2002',

    },
    
    'Toonami TOM2':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/CN/',
            'promos_cn':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/',
            'promos_ccf':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/CCF/Powerhouse Fridays/',
            'promos_toonami':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Promo_Commercials/TOM2/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Bumps/TOM2/',
            'credits':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Credits/',
            'long_promo':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Promo_Commercials/Long Promos/TOM2/',
            'vg':'/data/media/block_media/Archived Bumps & Commercials/Toonami/VG_Reviews/TOM2/',
        },
        'intro':'/data/media/block_media/Archived Bumps & Commercials/Toonami/TOM2 Intro.mp4',
        'outro':'/data/media/block_media/Archived Bumps & Commercials/Toonami/TOM2 Outro.mp4',
        'logo':'/unraid-scripts/logo/logo_Cartoon Network.png',
        'eras':{
            'Sailor Moon':{
                'All':np.arange(0,999)
            },
            'Yu Yu Hakusho':{
                'Intro':np.arange(0,15),
                'Tower':np.arange(15,26),
                'Early Tourney':np.arange(26,45),
            },
            'Batman Beyond':{
                'All':np.arange(0,999)
            },
            'Dragonball':{
                'All':np.arange(0,999)
            },
            'DBZ':{
                'Saiyan':np.arange(0,39),
                'Namek':np.arange(39,67),
                'Ginyu':np.arange(67,74),
                'Frieza':np.arange(74,107),
                'Garlic Jr':np.arange(107,117),
                'Trunks':np.arange(117,125),
                'Android':np.arange(126,139),
                'Imperfect':np.arange(139,152),
                'Cell':np.arange(152,194),
                'Saiyaman':np.arange(194,209),
                'World Tournament':np.arange(209,219),
                'Babidi':np.arange(220,231),
                'Buu':np.arange(231,253),
            },
            'Gundam Wing':{
                'All':np.arange(0,999)
            },
        },
    },
    
    'Toonami TOM3.5':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/CN/',
            'promos_cn':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/',
            'promos_ccf':'/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Promo_Commercials/CCF/Powerhouse Fridays/',
            'promos_toonami':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Promo_Commercials/TOM3.5/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Bumps/TOM3.5/',
            'credits':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Credits/',
            'long_promo':'/data/media/block_media/Archived Bumps & Commercials/Toonami/Promo_Commercials/Long Promos/TOM3.5/',
            'vg':'/data/media/block_media/Archived Bumps & Commercials/Toonami/VG_Reviews/TOM3.5/',
        },
        'intro':'/data/media/block_media/Archived Bumps & Commercials/Toonami/TOM3.5 Intro.mp4',
        'outro':'/data/media/block_media/Archived Bumps & Commercials/Toonami/TOM3.5 Outro.mp4',
        'logo':'/unraid-scripts/logo/logo_cn.png',
    },
    
    'FOX':{
        'clips':{
            'commercials':'/data/media/block_media/Archived Bumps & Commercials/Commercials/FOX/',
            'promos':'/data/media/block_media/Archived Bumps & Commercials/FOX/Promos/',
            'bumps':'/data/media/block_media/Archived Bumps & Commercials/FOX/Bumps/',
        },
        'logo':'/unraid-scripts/logo/logo_FOX.png',
    },
    
    #Placeholder dictionary - you don't actually have to put anything here
    'Custom':{
    }
            
    
}

type_dict={
    'Dick Van Dyke':'serial',
    'Family Guy':'episodic',
    'Futurama':'episodic',
    'Get Smart':'serial',
    'Happy Days':'serial',
    'King of the Hill':'serial',
    'Malcom in the Middle':'serial',
    'Mary Tyler Moore':'serial',
    'Robot Chicken':'episodic',
    'Harvey Birdman':'episodic',
    'Inuyasha':'serial',
    'Cowboy Bebop':'serial',
    'Case Closed':'serial',
    'Simpsons':'episodic',
    'The Munsters':'serial',
    'The Wonder Years':'serial',
    'X Files':'serial',
    'Powerpuff Girls':'episodic',
    'Ed Edd n Eddy':'episodic',
    'Camp Lazlo':'episodic',
    'Johnny Bravo':'episodic',
    'Dexters Laboratory':'episodic',
    'Courage the Cowardly Dog':'episodic',
    'New Scooby Doo Movies':'episodic',
    'Cow and Chicken':'episodic',
    'Codename Kids Next Door':'episodic',
    'The Grim Adventures of Billy and Mandy':'episodic',
    'Samurai Jack':'episodic',
    'Jetsons':'episodic',
    'Atom Ant':'episodic',
    'Flintstones':'episodic',
    'Huckleberry Hound':'episodic',
    'Yogi Bear':'episodic',
    'Quickdraw Mcgraw':'episodic',
    'Metalocalypse':'serial',
    'Squidbillies':'episodic',
    'Space Ghost Coast To Coast':'episodic',
    'Tom Goes To The Mayor':'episodic',
    'Sealab 2021':'episodic',
    'American Dad':'episodic',
    'Boondocks':'episodic',
    'Venture Bros':'serial',
    'Home Movies':'episodic',
    'Taxi':'serial',
    'Bob Newhart':'serial',
    'F Troop':'episodic',
    'Bewitched':'episodic', 
    'Sailor Moon':'serial',
    'Yu Yu Hakusho':'serial',
    'Batman Beyond':'serial',
    'Dragonball':'serial',
    'DBZ':'serial',
    'Gundam Wing':'serial',
    'Frisky Dingo':'serial',
    'Aqua Teen Hunger Force':'episodic',
    'Lupin the Third':'serial',
    'Wolfs Rain':'serial',
}


tv_ratings={
    'path':'/unraid-scripts/logo/',
    'American Dad':'tv_14.png',
    'Aqua Teen Hunger Force':'tv_ma.png',
    'Boondocks':'tv_ma.png',
    'Case Closed':'tv_14.png',
    'Cowboy Bebop':'tv_14.png',
    'Cromartie':'tv_14.png',
    'Family Guy':'tv_ma.png',
    'Frisky Dingo':'tv_ma.png',
    'Fullmetal Alchemist':'tv_pg.png',
    'Futurama':'tv_14.png',
    'Ghost in the Shell Stand Alone Complex':'tv_ma.png',
    'Great Teacher Onizuka':'tv_ma.png',
    'Harvey Birdman':'tv_ma.png',
    'Home Movies':'tv_14.png',
    'Inuyasha':'tv_14.png',
    'Lupin the Third':'tv_14.png',
    'Metalocalypse':'tv_ma.png',
    'Mission Hill':'tv_14.png',
    'Oblongs':'tv_14.png',
    'Robot Chicken':'tv_ma.png',
    'Samurai Champloo':'tv_ma.png',
    'Sealab 2021':'tv_14.png',
    'Space Ghost Coast to Coast':'tv_14.png',
    'Squidbillies':'tv_ma.png',
    'Superjail':'tv_ma.png',
    'The Big O':'tv_pg.png',
    'The Brak Show':'tv_pg.png',
    'Tom Goes To The Mayor':'tv_14.png',
    'Trigun':'tv_14.png',
    'Venture Bros':'tv_14.png',
    'Wolfs Rain':'tv_14.png',
    'Camp Lazlo':'tv_y7.png',
    'Codename Kids Next Door':'tv_y7.png',
    'Courage the Cowardly Dog':'tv_y7.png',
    'Cow and Chicken':'tv_pg.png',
    'Dexters Laboratory':'tv_y7.png',
    'Duck Dodgers':'tv_y7.png',
    'Ed Edd n Eddy':'tv_y7.png',
    'Evil Con Carne':'tv_y7.png',
    'Fosters Home for Imaginary Friends':'tv_y7.png',
    'Hi Hi Puffy AmiYumi':'tv_y7.png',
    'I Am Weasel':'tv_y7.png',
    'Johnny Bravo':'tv_y7.png',
    'Juniper Lee':'tv_y7.png',
    'Looney Tunes':'tv_y7.png',
    'Mike Lu and Og':'tv_y7.png',
    'Powerpuff Girls':'tv_y7.png',
    'Samurai Jack':'tv_pg.png',
    'Sheep in the Big City':'tv_y7.png',
    'The Grim Adventures of Billy and Mandy':'tv_y7fv.png',
    'Time Squad':'tv_y7.png',
    'Tom and Jerry':'tv_y7.png',
    'Toonheads':'tv_g.png',
    'What A Cartoon':'tv_g.png',
    'Whatever Happened to Robot Jones':'tv_y7.png',
    'King of the Hill':'tv_14.png',
    'Malcom in the Middle':'tv_pg.png',
    'Simpsons':'tv_14.png',
    'X Files':'tv_14.png',
    'Animaniacs':'tv_pg.png',
    'Cardcaptors':'tv_y7.png',
    'MiB':'tv_y7.png',
    'Pokemon':'tv_y7.png',
    'Code Lyoko':'tv_y7.png',
    'Static Shock':'tv_y7.png',
    'Teen Titans':'tv_y7fv.png',
    'Teenage Mutant Ninja Turtles':'tv_y7.png',
    'Totally Spies':'tv_y7.png',
    'Bewitched':'tv_g.png',
    'Bob Newhart':'tv_g.png',
    'Cosby Show':'tv_g.png',
    'Dick Van Dyke':'tv_g.png',
    'F Troop':'tv_g.png',
    'Get Smart':'tv_g.png',
    'Happy Days':'tv_g.png',
    'Mary Tyler Moore':'tv_g.png',
    'Taxi':'tv_g.png',
    'The Munsters':'tv_g.png',
    'The Wonder Years':'tv_g.png',
    'Batman Beyond':'tv_y7.png',
    'Bobobo':'tv_y7fv.png',
    'Clone Wars':'tv_y7.png',
    'Cyborg 009':'tv_14.png',
    'DBZ':'tv_pg.png',
    'Dragonball':'tv_14.png',
    'G Gundam':'tv_pg.png',
    'Gundam Wing':'tv_pg.png',
    'Hamtaro':'tv_y7.png',
    'He Man':'tv_y7.png',
    'Jackie Chan Adventures':'tv_y7.png',
    'Justice League':'tv_pg.png',
    'Justice League Unlimited':'tv_pg.png',
    'Megas XLR':'tv_y7fv.png',
    'Naruto':'tv_pg.png',
    'Outlaw Star':'tv_pg.png',
    'Reboot':'tv_y7.png',
    'Ruroni Kenshin':'tv_14.png',
    'Sailor Moon':'tv_y7.png',
    'Transformers Armada':'tv_y7.png',
    'Yu Yu Hakusho':'tv_pg.png',
    'Zatch Bell':'tv_y7.png',
}

show_groups={
    'Adult Swim_1':['Family Guy','Futurama','American Dad'],
    'Adult Swim_2':['Squidbillies','Frisky Dingo','Aqua Teen Hunger Force',
                   'Tom Goes To The Mayor','Sealab 2021',
                   'Robot Chicken','Metalocalypse','Harvey Birdman'],
    'Adult Swim_3':['Boondocks','Home Movies','Case Closed','Lupin the Third'],
    'Nick at Nite_1':['Bewitched','Dick Van Dyke','Happy Days','Taxi',
                      'Bob Newhart','F Troop','Mary Tyler Moore',
                      'The Munsters','Get Smart','The Wonder Years'],
}
