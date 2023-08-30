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
        'Toonami TOM2':'/data/media/block_media/Broadcast_Shows/Toonami/',
        'Toonami TOM3.5':'/data/media/block_media/Broadcast_Shows/Toonami/',
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
                'Imperfect Cell':np.arange(139,152),
                'Perfect Cell':np.arange(152,165),
                'Cell':np.arange(165,194),
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
    'Gundam Wing':'serial'
}

show_groups={
    'Adult Swim_1':['Family Guy','Futurama','American Dad'],
    'Adult Swim_2':['Space Ghost Coast to Coast','Squidbillies',
                   'Tom Goes To The Mayor','Sealab 2021',
                   'Robot Chicken','Metalocalypse','Harvey Birdman'],
    'Adult Swim_3':['Boondocks','Home Movies','Case Closed','Venture Bros'],
    'Nick at Nite_1':['Bewitched','Dick Van Dyke','Happy Days','Taxi',
                      'Bob Newhart','F Troop','Mary Tyler Moore',
                      'The Munsters','Get Smart','The Wonder Years'],
}
