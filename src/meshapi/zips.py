from dataclasses import dataclass

@dataclass
class NYCZipCodes():
    def match_zip(self, zip):
        return any(zip in a for a in [self.bronx, self.new_york, self.kings, self.queens, self.richmond])

    bronx = [
        10466,
        10468,
        10469,
        10465,
        10456,
        10451,
        10461,
        10471,
        10460,
        10454,
        10457,
        10473,
        10452,
        10474,
        10459,
        10467,
        10463,
        10472,
        10464,
        10455,
        10470,
        10462,
        10458,
        10453,
        10475,
    ]

    new_york = [
        10029,
        10043,
        10075,
        10024,
        10005,
        10016,
        10011,
        10018,
        10017,
        10009,
        10019,
        10002,
        10013,
        10034,
        10031,
        10006,
        10001,
        10003,
        10040,
        10004,
        10021,
        10007,
        10010,
        10032,
        10036,
        10022,
        10037,
        10060,
        10008,
        10069,
        10020,
        10027,
        10039,
        10012,
        10026,
        10033,
        10035,
        10038,
        10028,
        10044,
        10065,
        10081,
        10025,
        10080,
        10055,
        10023,
        10014,
        10041,
        10030,
        10045,
    ]

    kings = [
        11234,
        11233,
        11221,
        11232,
        11243,
        11229,
        11256,
        11241,
        11224,
        11236,
        11247,
        11220,
        11225,
        11237,
        11206,
        11216,
        11214,
        11239,
        11245,
        11210,
        11207,
        11219,
        11249,
        11209,
        11223,
        11251,
        11238,
        11230,
        11211,
        11231,
        11228,
        11205,
        11203,
        11202,
        11212,
        11208,
        11416,
        11217,
        11201,
        11215,
        11218,
        11222,
        11235,
        11242,
        11213,
        11252,
        11204,
        11226,
    ]

    queens = [
        11368,
        11412,
        11120,
        11361,
        11352,
        11386,
        11001,
        11104,
        11375,
        11357,
        11414,
        11364,
        11105,
        11377,
        11416,
        11411,
        11365,
        11208,
        11373,
        11415,
        11380,
        11354,
        11366,
        11372,
        11101,
        11351,
        11374,
        11040,
        11005,
        11363,
        11358,
        11106,
        11362,
        11370,
        11367,
        11004,
        11369,
        11385,
        11102,
        11360,
        11103,
        11355,
        11379,
        11359,
        11109,
        11413,
        11371,
        11405,
        11378,
        11356,
    ]

    richmond = [
        10314,
        10313,
        10312,
        10302,
        10311,
        10301,
        10310,
        10307,
        10304,
        10308,
        10305,
        10303,
        10309,
        10306,
    ]
