/**
 * data.js — 자동 생성 파일 (db/build_db.py 가 SQLite DB로부터 생성)
 * 직접 수정하지 마세요. 데이터는 db/seed 또는 DB에서 수정 후 빌드하세요.
 */
const SPECIALTIES = {
  "정신건강의학과": [
    "기분장애(우울/조울)",
    "불안·공황장애",
    "조현병·정신증",
    "중독(알코올/도박/게임)",
    "노인정신(치매/섬망)",
    "소아청소년정신",
    "수면의학",
    "정신신체의학",
    "강박·외상(PTSD)",
    "자살예방·정신응급"
  ]
};

const HOSPITALS = [
  {
    "id": "p1",
    "name": "국립서울정신건강병원",
    "type": "정신병원(공공)",
    "address": "서울특별시 광진구 용마산로 127",
    "lat": 37.5589,
    "lng": 127.0884,
    "phone": "02-2204-0114",
    "beds": 480,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": true,
    "transit": "지하철 7호선 중곡역 도보 7분",
    "ambulanceBay": true,
    "transferDesk": true,
    "closedWard": true,
    "inpatient": true,
    "psychER": true,
    "dayHospital": true,
    "avgWaitMin": 30,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "김현수",
        "title": "진료부장",
        "specialty": "정신건강의학과",
        "subspecialty": "조현병·정신증",
        "school": "서울대학교 의과대학",
        "gradYear": 1998,
        "training": "서울대학교병원 정신건강의학과 전공의/전임의",
        "career": [
          "만성 조현병 입원치료 전문",
          "정신응급 대응 체계 운영",
          "대한신경정신의학회 정회원"
        ],
        "reputation": 4.6,
        "reviews": 142
      },
      {
        "name": "이정민",
        "title": "정신응급팀장",
        "specialty": "정신건강의학과",
        "subspecialty": "자살예방·정신응급",
        "school": "연세대학교 의과대학",
        "gradYear": 2003,
        "training": "세브란스병원 정신건강의학과 전공의/전임의",
        "career": [
          "24시간 정신응급 진료",
          "자살위기 개입(C-SSRS)",
          "응급입원·행정입원 전원 코디네이션"
        ],
        "reputation": 4.7,
        "reviews": 188
      }
    ]
  },
  {
    "id": "p10",
    "name": "강북힐링정신건강의학과의원",
    "type": "정신건강의학과의원",
    "address": "서울특별시 강북구 도봉로 235",
    "lat": 37.6376,
    "lng": 127.0256,
    "phone": "02-989-3375",
    "beds": 0,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": false,
    "transit": "지하철 4호선 수유역 도보 4분",
    "ambulanceBay": false,
    "transferDesk": false,
    "closedWard": false,
    "inpatient": false,
    "psychER": false,
    "dayHospital": false,
    "avgWaitMin": 14,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "배수민",
        "title": "원장",
        "specialty": "정신건강의학과",
        "subspecialty": "정신신체의학",
        "school": "부산대학교 의과대학",
        "gradYear": 2008,
        "training": "분당서울대학교병원 정신건강의학과 전공의/전임의",
        "career": [
          "스트레스성 신체증상·화병 진료",
          "만성통증 정신건강 협진",
          "대한정신신체의학회 회원"
        ],
        "reputation": 4.6,
        "reviews": 119
      }
    ]
  },
  {
    "id": "p11",
    "name": "수원중앙대학교병원 정신건강의학과",
    "type": "종합병원 정신건강의학과",
    "address": "경기도 수원시 영통구 월드컵로 164",
    "lat": 37.2782,
    "lng": 127.0435,
    "phone": "031-219-5114",
    "beds": 90,
    "er": true,
    "erLevel": "지역응급의료센터",
    "icu": false,
    "parking": true,
    "transit": "분당선 청명역 도보 10분",
    "ambulanceBay": true,
    "transferDesk": true,
    "closedWard": true,
    "inpatient": true,
    "psychER": true,
    "dayHospital": false,
    "avgWaitMin": 28,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "서지안",
        "title": "교수",
        "specialty": "정신건강의학과",
        "subspecialty": "자살예방·정신응급",
        "school": "아주대학교 의과대학",
        "gradYear": 2003,
        "training": "아주대학교병원 정신건강의학과 전공의/전임의",
        "career": [
          "응급실 기반 정신응급 협진",
          "자살시도자 사후관리(사례관리)",
          "대한신경정신의학회 정회원"
        ],
        "reputation": 4.7,
        "reviews": 176
      }
    ]
  },
  {
    "id": "p2",
    "name": "마음편한신경정신과의원",
    "type": "정신건강의학과의원",
    "address": "서울특별시 강남구 테헤란로 311",
    "lat": 37.5045,
    "lng": 127.0419,
    "phone": "02-558-0079",
    "beds": 0,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": true,
    "transit": "지하철 2호선 역삼역 도보 3분",
    "ambulanceBay": false,
    "transferDesk": false,
    "closedWard": false,
    "inpatient": false,
    "psychER": false,
    "dayHospital": false,
    "avgWaitMin": 15,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "박서진",
        "title": "원장",
        "specialty": "정신건강의학과",
        "subspecialty": "불안·공황장애",
        "school": "성균관대학교 의과대학",
        "gradYear": 2008,
        "training": "삼성서울병원 정신건강의학과 전공의/전임의",
        "career": [
          "공황장애·사회불안 인지행동치료(CBT)",
          "직장인 스트레스 클리닉",
          "대한불안의학회 회원"
        ],
        "reputation": 4.8,
        "reviews": 264
      }
    ]
  },
  {
    "id": "p3",
    "name": "서울맑은정신건강의학과병원",
    "type": "정신병원",
    "address": "서울특별시 노원구 동일로 1234",
    "lat": 37.6491,
    "lng": 127.0628,
    "phone": "02-933-7575",
    "beds": 220,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": true,
    "transit": "지하철 7호선 마들역 도보 6분",
    "ambulanceBay": true,
    "transferDesk": true,
    "closedWard": true,
    "inpatient": true,
    "psychER": false,
    "dayHospital": true,
    "avgWaitMin": 22,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "정유나",
        "title": "병원장",
        "specialty": "정신건강의학과",
        "subspecialty": "기분장애(우울/조울)",
        "school": "가톨릭대학교 의과대학",
        "gradYear": 2002,
        "training": "서울성모병원 정신건강의학과 전공의/전임의",
        "career": [
          "난치성 우울증 입원치료",
          "전기경련치료(ECT) 운영",
          "대한우울조울병학회 정회원"
        ],
        "reputation": 4.5,
        "reviews": 131
      },
      {
        "name": "한지호",
        "title": "과장",
        "specialty": "정신건강의학과",
        "subspecialty": "노인정신(치매/섬망)",
        "school": "한양대학교 의과대학",
        "gradYear": 2007,
        "training": "한양대학교병원 정신건강의학과 전공의",
        "career": [
          "노인 우울·치매 동반 입원치료",
          "섬망 관리",
          "대한노인정신의학회 회원"
        ],
        "reputation": 4.4,
        "reviews": 97
      }
    ]
  },
  {
    "id": "p4",
    "name": "새봄소아청소년정신건강의학과의원",
    "type": "정신건강의학과의원",
    "address": "서울특별시 양천구 목동중앙로 86",
    "lat": 37.5266,
    "lng": 126.8757,
    "phone": "02-2654-0420",
    "beds": 0,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": false,
    "transit": "지하철 5호선 목동역 도보 4분",
    "ambulanceBay": false,
    "transferDesk": false,
    "closedWard": false,
    "inpatient": false,
    "psychER": false,
    "dayHospital": false,
    "avgWaitMin": 18,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "오하늘",
        "title": "원장",
        "specialty": "정신건강의학과",
        "subspecialty": "소아청소년정신",
        "school": "이화여자대학교 의과대학",
        "gradYear": 2009,
        "training": "서울대학교어린이병원 소아청소년정신 전임의",
        "career": [
          "ADHD·틱·발달 클리닉",
          "청소년 우울·불안 평가",
          "대한소아청소년정신의학회 회원"
        ],
        "reputation": 4.7,
        "reviews": 203
      }
    ]
  },
  {
    "id": "p5",
    "name": "한울중독정신건강의학과병원",
    "type": "정신병원(중독전문)",
    "address": "경기도 의왕시 오전로 159",
    "lat": 37.3447,
    "lng": 126.9683,
    "phone": "031-340-5000",
    "beds": 180,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": true,
    "transit": "지하철 1호선 의왕역 차량 8분",
    "ambulanceBay": true,
    "transferDesk": true,
    "closedWard": true,
    "inpatient": true,
    "psychER": false,
    "dayHospital": true,
    "avgWaitMin": 25,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "신동욱",
        "title": "병원장",
        "specialty": "정신건강의학과",
        "subspecialty": "중독(알코올/도박/게임)",
        "school": "중앙대학교 의과대학",
        "gradYear": 2001,
        "training": "국립법무병원·중앙대학교병원 정신건강의학과 전공의",
        "career": [
          "알코올 해독·재활 입원프로그램",
          "도박·게임 중독 클리닉",
          "한국중독정신의학회 정회원"
        ],
        "reputation": 4.5,
        "reviews": 116
      }
    ]
  },
  {
    "id": "p6",
    "name": "연세마음정신건강의학과의원",
    "type": "정신건강의학과의원",
    "address": "서울특별시 서대문구 신촌로 83",
    "lat": 37.5559,
    "lng": 126.9368,
    "phone": "02-313-0091",
    "beds": 0,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": false,
    "transit": "지하철 2호선 신촌역 도보 2분",
    "ambulanceBay": false,
    "transferDesk": false,
    "closedWard": false,
    "inpatient": false,
    "psychER": false,
    "dayHospital": false,
    "avgWaitMin": 12,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "윤소희",
        "title": "원장",
        "specialty": "정신건강의학과",
        "subspecialty": "수면의학",
        "school": "고려대학교 의과대학",
        "gradYear": 2010,
        "training": "고려대학교안암병원 정신건강의학과 전공의/전임의",
        "career": [
          "불면증 인지행동치료(CBT-I)",
          "수면다원검사 판독",
          "대한수면의학회 회원"
        ],
        "reputation": 4.6,
        "reviews": 158
      }
    ]
  },
  {
    "id": "p7",
    "name": "분당온정신건강의학과병원",
    "type": "정신병원",
    "address": "경기도 성남시 분당구 성남대로 343",
    "lat": 37.3825,
    "lng": 127.1186,
    "phone": "031-712-2275",
    "beds": 160,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": true,
    "transit": "분당선 서현역 도보 9분",
    "ambulanceBay": true,
    "transferDesk": true,
    "closedWard": true,
    "inpatient": true,
    "psychER": true,
    "dayHospital": true,
    "avgWaitMin": 20,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "강민재",
        "title": "병원장",
        "specialty": "정신건강의학과",
        "subspecialty": "조현병·정신증",
        "school": "울산대학교 의과대학",
        "gradYear": 2004,
        "training": "서울아산병원 정신건강의학과 전공의/전임의",
        "career": [
          "초발 정신증 조기중재",
          "급성기 보호병동 운영",
          "대한조현병학회 정회원"
        ],
        "reputation": 4.6,
        "reviews": 149
      },
      {
        "name": "임가은",
        "title": "과장",
        "specialty": "정신건강의학과",
        "subspecialty": "강박·외상(PTSD)",
        "school": "경희대학교 의과대학",
        "gradYear": 2011,
        "training": "경희대학교병원 정신건강의학과 전공의",
        "career": [
          "외상후스트레스(PTSD)·강박장애 치료",
          "EMDR 시행",
          "대한정신건강의학회 회원"
        ],
        "reputation": 4.7,
        "reviews": 121
      }
    ]
  },
  {
    "id": "p8",
    "name": "인천나래정신건강의학과의원",
    "type": "정신건강의학과의원",
    "address": "인천광역시 남동구 구월로 234",
    "lat": 37.4486,
    "lng": 126.7019,
    "phone": "032-462-7140",
    "beds": 0,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": true,
    "transit": "인천1호선 예술회관역 도보 5분",
    "ambulanceBay": false,
    "transferDesk": false,
    "closedWard": false,
    "inpatient": false,
    "psychER": false,
    "dayHospital": true,
    "avgWaitMin": 16,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "조은별",
        "title": "원장",
        "specialty": "정신건강의학과",
        "subspecialty": "기분장애(우울/조울)",
        "school": "인하대학교 의과대학",
        "gradYear": 2009,
        "training": "인하대학교병원 정신건강의학과 전공의/전임의",
        "career": [
          "우울·양극성장애 외래관리",
          "낮병원 재활프로그램",
          "대한우울조울병학회 회원"
        ],
        "reputation": 4.5,
        "reviews": 134
      }
    ]
  },
  {
    "id": "p9",
    "name": "고양늘봄정신건강의학과병원",
    "type": "정신병원",
    "address": "경기도 고양시 덕양구 화중로 110",
    "lat": 37.6358,
    "lng": 126.8326,
    "phone": "031-963-8275",
    "beds": 200,
    "er": false,
    "erLevel": null,
    "icu": false,
    "parking": true,
    "transit": "지하철 3호선 화정역 도보 8분",
    "ambulanceBay": true,
    "transferDesk": true,
    "closedWard": true,
    "inpatient": true,
    "psychER": false,
    "dayHospital": true,
    "avgWaitMin": 24,
    "specialties": [
      "정신건강의학과"
    ],
    "doctors": [
      {
        "name": "문채원",
        "title": "병원장",
        "specialty": "정신건강의학과",
        "subspecialty": "노인정신(치매/섬망)",
        "school": "건국대학교 의과대학",
        "gradYear": 2005,
        "training": "건국대학교병원 정신건강의학과 전공의/전임의",
        "career": [
          "치매·행동심리증상(BPSD) 입원치료",
          "노인 정신건강 방문진료",
          "대한노인정신의학회 정회원"
        ],
        "reputation": 4.4,
        "reviews": 88
      }
    ]
  }
];

const SPECIALISTS = [
  {
    "id": "knpa_001",
    "name": "김태영",
    "gender": "M",
    "hospitalId": null,
    "subspecialty": "불안·공황장애",
    "reputation": 0.0,
    "reviews": 0,
    "license": {
      "type": "의사면허",
      "no": "제51234호",
      "year": null
    },
    "boardCert": {
      "certNo": "정신건강의학과-2008-000777",
      "year": 2008,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "서울대학교",
        "year": 2002,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "레지던트",
        "hospital": "서울대학교병원",
        "start_year": 2003,
        "end_year": 2007
      }
    ],
    "positions": [
      {
        "org": "서울행복정신건강의학과의원",
        "title": "전문의",
        "start_year": null,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [],
    "publications": [],
    "certifications": [],
    "interests": [
      "불안·공황장애"
    ],
    "sources": [
      {
        "field": "roster",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 수집·정합",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "affiliation",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "소속기관(병원DB 미등록)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "medium"
      }
    ]
  },
  {
    "id": "knpa_002",
    "name": "이수진",
    "gender": "F",
    "hospitalId": null,
    "subspecialty": "기분장애(우울/조울)",
    "reputation": 0.0,
    "reviews": 0,
    "license": {
      "type": "의사면허",
      "no": "제60111호",
      "year": null
    },
    "boardCert": {
      "certNo": "정신건강의학과-2014-001580",
      "year": 2014,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "연세대학교",
        "year": 2008,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "레지던트",
        "hospital": "세브란스병원",
        "start_year": 2009,
        "end_year": 2013
      }
    ],
    "positions": [
      {
        "org": "마포평온정신건강의학과병원",
        "title": "전문의",
        "start_year": null,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [],
    "publications": [],
    "certifications": [],
    "interests": [
      "기분장애(우울/조울)"
    ],
    "sources": [
      {
        "field": "roster",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 수집·정합",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "affiliation",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "소속기관(병원DB 미등록)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "medium"
      }
    ]
  },
  {
    "id": "knpa_003",
    "name": "박민호",
    "gender": "M",
    "hospitalId": null,
    "subspecialty": "중독(알코올/도박/게임)",
    "reputation": 0.0,
    "reviews": 0,
    "license": {
      "type": "의사면허",
      "no": "제47002호",
      "year": null
    },
    "boardCert": {
      "certNo": "정신건강의학과-2005-000510",
      "year": 2005,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "고려대학교",
        "year": 1999,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "레지던트",
        "hospital": "고려대학교구로병원",
        "start_year": 2000,
        "end_year": 2004
      }
    ],
    "positions": [
      {
        "org": "한빛정신건강의학과의원",
        "title": "전문의",
        "start_year": null,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [],
    "publications": [],
    "certifications": [],
    "interests": [
      "중독(알코올/도박/게임)"
    ],
    "sources": [
      {
        "field": "roster",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 수집·정합",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "affiliation",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "소속기관(병원DB 미등록)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "medium"
      }
    ]
  },
  {
    "id": "knpa_004",
    "name": "박민호",
    "gender": "M",
    "hospitalId": null,
    "subspecialty": "조현병·정신증",
    "reputation": 0.0,
    "reviews": 0,
    "license": {
      "type": "의사면허",
      "no": "제72540호",
      "year": null
    },
    "boardCert": {
      "certNo": "정신건강의학과-2018-003220",
      "year": 2018,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "부산대학교",
        "year": 2012,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "레지던트",
        "hospital": "부산대학교병원",
        "start_year": 2013,
        "end_year": 2017
      }
    ],
    "positions": [
      {
        "org": "동래마음정신건강의학과의원",
        "title": "전문의",
        "start_year": null,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [],
    "publications": [],
    "certifications": [],
    "interests": [
      "조현병·정신증"
    ],
    "sources": [
      {
        "field": "roster",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 수집·정합",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "affiliation",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "소속기관(병원DB 미등록)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "medium"
      }
    ]
  },
  {
    "id": "psy001",
    "name": "김현수",
    "gender": "M",
    "hospitalId": "p1",
    "subspecialty": "조현병·정신증",
    "reputation": 4.6,
    "reviews": 142,
    "license": {
      "type": "의사면허",
      "no": "제45012호",
      "year": 1995
    },
    "boardCert": {
      "certNo": "정신건강의학과-2003-000457",
      "year": 2003,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "서울대학교 의과대학",
        "year": 1998,
        "thesis": null
      },
      {
        "degree": "의학박사",
        "school": "서울대학교 대학원",
        "year": 2009,
        "thesis": "조현병 환자의 인지기능과 예후"
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "서울대학교병원",
        "start_year": 1998,
        "end_year": 1999
      },
      {
        "role": "레지던트",
        "hospital": "서울대학교병원 정신건강의학과",
        "start_year": 1999,
        "end_year": 2003
      },
      {
        "role": "전임의",
        "hospital": "서울대학교병원 정신건강의학과",
        "start_year": 2003,
        "end_year": 2005
      }
    ],
    "positions": [
      {
        "org": "국립서울정신건강병원",
        "title": "진료부장",
        "start_year": 2015,
        "end_year": null,
        "is_current": 1
      },
      {
        "org": "서울대학교병원 정신건강의학과",
        "title": "임상교수",
        "start_year": 2005,
        "end_year": 2015,
        "is_current": 0
      }
    ],
    "societies": [
      {
        "name": "대한신경정신의학회",
        "role": "정회원"
      },
      {
        "name": "대한조현병학회",
        "role": "이사"
      }
    ],
    "publications": [
      {
        "title": "Cognitive function and long-term outcome in schizophrenia",
        "journal": "Journal of Korean Neuropsychiatric Association",
        "year": 2018,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2006
      }
    ],
    "interests": [
      "조현병·정신증",
      "정신응급",
      "급성기 입원치료"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "국립서울정신건강병원 의료진 소개",
        "method": "기관 홈페이지 수집",
        "url": "https://www.ncmh.go.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "publications",
        "source": "KoreaMed / PubMed",
        "method": "저자명 검색",
        "url": "https://koreamed.org",
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "reputation",
        "source": "진료 후기 집계",
        "method": "리뷰 플랫폼 집계",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "low"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy002",
    "name": "이정민",
    "gender": "F",
    "hospitalId": "p1",
    "subspecialty": "자살예방·정신응급",
    "reputation": 4.7,
    "reviews": 188,
    "license": {
      "type": "의사면허",
      "no": "제48230호",
      "year": 2000
    },
    "boardCert": {
      "certNo": "정신건강의학과-2008-001123",
      "year": 2008,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "연세대학교 의과대학",
        "year": 2003,
        "thesis": null
      },
      {
        "degree": "의학석사",
        "school": "연세대학교 대학원",
        "year": 2010,
        "thesis": "응급실 내원 자살시도자의 임상특성"
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "세브란스병원",
        "start_year": 2003,
        "end_year": 2004
      },
      {
        "role": "레지던트",
        "hospital": "세브란스병원 정신건강의학과",
        "start_year": 2004,
        "end_year": 2008
      },
      {
        "role": "전임의",
        "hospital": "세브란스병원 정신건강의학과",
        "start_year": 2008,
        "end_year": 2010
      }
    ],
    "positions": [
      {
        "org": "국립서울정신건강병원",
        "title": "정신응급팀장",
        "start_year": 2018,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한신경정신의학회",
        "role": "정회원"
      },
      {
        "name": "한국자살예방협회",
        "role": "회원"
      }
    ],
    "publications": [
      {
        "title": "Clinical characteristics of suicide attempters in the emergency department",
        "journal": "Journal of Korean Medical Science",
        "year": 2016,
        "role": "공저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2011
      },
      {
        "name": "자살예방 게이트키퍼 강사",
        "year": 2015
      }
    ],
    "interests": [
      "정신응급",
      "자살위기개입",
      "재난정신건강"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "국립서울정신건강병원 의료진 소개",
        "method": "기관 홈페이지 수집",
        "url": "https://www.ncmh.go.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "publications",
        "source": "KoreaMed / PubMed",
        "method": "저자명 검색",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy003",
    "name": "박서진",
    "gender": "M",
    "hospitalId": "p2",
    "subspecialty": "불안·공황장애",
    "reputation": 4.8,
    "reviews": 264,
    "license": {
      "type": "의사면허",
      "no": "제51890호",
      "year": 2005
    },
    "boardCert": {
      "certNo": "정신건강의학과-2013-002210",
      "year": 2013,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "성균관대학교 의과대학",
        "year": 2008,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "삼성서울병원",
        "start_year": 2008,
        "end_year": 2009
      },
      {
        "role": "레지던트",
        "hospital": "삼성서울병원 정신건강의학과",
        "start_year": 2009,
        "end_year": 2013
      },
      {
        "role": "전임의",
        "hospital": "삼성서울병원 정신건강의학과",
        "start_year": 2013,
        "end_year": 2014
      }
    ],
    "positions": [
      {
        "org": "마음편한신경정신과의원",
        "title": "원장",
        "start_year": 2016,
        "end_year": null,
        "is_current": 1
      },
      {
        "org": "삼성서울병원 정신건강의학과",
        "title": "임상강사",
        "start_year": 2014,
        "end_year": 2016,
        "is_current": 0
      }
    ],
    "societies": [
      {
        "name": "대한불안의학회",
        "role": "회원"
      },
      {
        "name": "대한인지행동치료학회",
        "role": "회원"
      }
    ],
    "publications": [
      {
        "title": "CBT outcomes for panic disorder in primary psychiatric care",
        "journal": "Anxiety and Mood",
        "year": 2019,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2016
      }
    ],
    "interests": [
      "공황장애",
      "사회불안장애",
      "인지행동치료(CBT)"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "의원 홈페이지 의료진 소개",
        "method": "기관 홈페이지 수집",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "reputation",
        "source": "진료 후기 집계",
        "method": "리뷰 플랫폼 집계",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "low"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy004",
    "name": "정유나",
    "gender": "F",
    "hospitalId": "p3",
    "subspecialty": "기분장애(우울/조울)",
    "reputation": 4.5,
    "reviews": 131,
    "license": {
      "type": "의사면허",
      "no": "제44551호",
      "year": 1999
    },
    "boardCert": {
      "certNo": "정신건강의학과-2007-000912",
      "year": 2007,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "가톨릭대학교 의과대학",
        "year": 2002,
        "thesis": null
      },
      {
        "degree": "의학박사",
        "school": "가톨릭대학교 대학원",
        "year": 2013,
        "thesis": "치료저항성 우울증의 ECT 반응 예측인자"
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "서울성모병원",
        "start_year": 2002,
        "end_year": 2003
      },
      {
        "role": "레지던트",
        "hospital": "서울성모병원 정신건강의학과",
        "start_year": 2003,
        "end_year": 2007
      },
      {
        "role": "전임의",
        "hospital": "서울성모병원 정신건강의학과",
        "start_year": 2007,
        "end_year": 2009
      }
    ],
    "positions": [
      {
        "org": "서울맑은정신건강의학과병원",
        "title": "병원장",
        "start_year": 2014,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한우울조울병학회",
        "role": "정회원"
      },
      {
        "name": "대한신경정신의학회",
        "role": "정회원"
      }
    ],
    "publications": [
      {
        "title": "Predictors of ECT response in treatment-resistant depression",
        "journal": "Journal of Affective Disorders",
        "year": 2015,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2010
      }
    ],
    "interests": [
      "난치성 우울증",
      "양극성장애",
      "전기경련치료(ECT)"
    ],
    "sources": [
      {
        "field": "publications",
        "source": "PubMed",
        "method": "저자명 검색",
        "url": "https://pubmed.ncbi.nlm.nih.gov",
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy005",
    "name": "한지호",
    "gender": "M",
    "hospitalId": "p3",
    "subspecialty": "노인정신(치매/섬망)",
    "reputation": 4.4,
    "reviews": 97,
    "license": {
      "type": "의사면허",
      "no": "제50677호",
      "year": 2004
    },
    "boardCert": {
      "certNo": "정신건강의학과-2012-001745",
      "year": 2012,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "한양대학교 의과대학",
        "year": 2007,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "한양대학교병원",
        "start_year": 2007,
        "end_year": 2008
      },
      {
        "role": "레지던트",
        "hospital": "한양대학교병원 정신건강의학과",
        "start_year": 2008,
        "end_year": 2012
      }
    ],
    "positions": [
      {
        "org": "서울맑은정신건강의학과병원",
        "title": "과장",
        "start_year": 2015,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한노인정신의학회",
        "role": "회원"
      }
    ],
    "publications": [],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2015
      }
    ],
    "interests": [
      "노인우울",
      "치매 행동심리증상(BPSD)",
      "섬망"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "병원 홈페이지 의료진 소개",
        "method": "기관 홈페이지 수집",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy006",
    "name": "오하늘",
    "gender": "F",
    "hospitalId": "p4",
    "subspecialty": "소아청소년정신",
    "reputation": 4.7,
    "reviews": 203,
    "license": {
      "type": "의사면허",
      "no": "제52140호",
      "year": 2006
    },
    "boardCert": {
      "certNo": "정신건강의학과-2014-002588",
      "year": 2014,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "이화여자대학교 의과대학",
        "year": 2009,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "이대목동병원",
        "start_year": 2009,
        "end_year": 2010
      },
      {
        "role": "레지던트",
        "hospital": "이대목동병원 정신건강의학과",
        "start_year": 2010,
        "end_year": 2014
      },
      {
        "role": "전임의",
        "hospital": "서울대학교어린이병원 소아청소년정신",
        "start_year": 2014,
        "end_year": 2016
      }
    ],
    "positions": [
      {
        "org": "새봄소아청소년정신건강의학과의원",
        "title": "원장",
        "start_year": 2018,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한소아청소년정신의학회",
        "role": "회원"
      }
    ],
    "publications": [
      {
        "title": "ADHD 아동의 실행기능과 학업성취",
        "journal": "소아청소년정신의학",
        "year": 2017,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2017
      },
      {
        "name": "소아청소년정신의학 인증의",
        "year": 2017
      }
    ],
    "interests": [
      "ADHD",
      "틱장애",
      "소아청소년 우울·불안"
    ],
    "sources": [
      {
        "field": "training",
        "source": "수련기관 전공의 이력",
        "method": "기관 자료 확인",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy007",
    "name": "신동욱",
    "gender": "M",
    "hospitalId": "p5",
    "subspecialty": "중독(알코올/도박/게임)",
    "reputation": 4.5,
    "reviews": 116,
    "license": {
      "type": "의사면허",
      "no": "제43388호",
      "year": 1998
    },
    "boardCert": {
      "certNo": "정신건강의학과-2006-000633",
      "year": 2006,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "중앙대학교 의과대학",
        "year": 2001,
        "thesis": null
      },
      {
        "degree": "의학박사",
        "school": "중앙대학교 대학원",
        "year": 2014,
        "thesis": "알코올사용장애의 재발 예측요인"
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "중앙대학교병원",
        "start_year": 2001,
        "end_year": 2002
      },
      {
        "role": "레지던트",
        "hospital": "중앙대학교병원 정신건강의학과",
        "start_year": 2002,
        "end_year": 2006
      }
    ],
    "positions": [
      {
        "org": "한울중독정신건강의학과병원",
        "title": "병원장",
        "start_year": 2013,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "한국중독정신의학회",
        "role": "정회원"
      },
      {
        "name": "대한신경정신의학회",
        "role": "정회원"
      }
    ],
    "publications": [
      {
        "title": "Relapse predictors in alcohol use disorder",
        "journal": "Journal of Korean Academy of Addiction Psychiatry",
        "year": 2016,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2009
      },
      {
        "name": "중독전문의(한국중독정신의학회)",
        "year": 2010
      }
    ],
    "interests": [
      "알코올 중독",
      "도박·게임 중독",
      "중독 재활"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "병원 홈페이지",
        "method": "기관 홈페이지 수집",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy008",
    "name": "윤소희",
    "gender": "F",
    "hospitalId": "p6",
    "subspecialty": "수면의학",
    "reputation": 4.6,
    "reviews": 158,
    "license": {
      "type": "의사면허",
      "no": "제53299호",
      "year": 2007
    },
    "boardCert": {
      "certNo": "정신건강의학과-2015-002901",
      "year": 2015,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "고려대학교 의과대학",
        "year": 2010,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "고려대학교안암병원",
        "start_year": 2010,
        "end_year": 2011
      },
      {
        "role": "레지던트",
        "hospital": "고려대학교안암병원 정신건강의학과",
        "start_year": 2011,
        "end_year": 2015
      },
      {
        "role": "전임의",
        "hospital": "고려대학교안암병원 수면의학",
        "start_year": 2015,
        "end_year": 2016
      }
    ],
    "positions": [
      {
        "org": "연세마음정신건강의학과의원",
        "title": "원장",
        "start_year": 2018,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한수면의학회",
        "role": "회원"
      }
    ],
    "publications": [
      {
        "title": "Efficacy of CBT-I in chronic insomnia",
        "journal": "Sleep Medicine and Psychophysiology",
        "year": 2018,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2018
      },
      {
        "name": "수면전문의(대한수면의학회)",
        "year": 2019
      }
    ],
    "interests": [
      "불면증",
      "수면다원검사",
      "일주기리듬장애"
    ],
    "sources": [
      {
        "field": "publications",
        "source": "KoreaMed",
        "method": "저자명 검색",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy009",
    "name": "강민재",
    "gender": "M",
    "hospitalId": "p7",
    "subspecialty": "조현병·정신증",
    "reputation": 4.6,
    "reviews": 149,
    "license": {
      "type": "의사면허",
      "no": "제49112호",
      "year": 2001
    },
    "boardCert": {
      "certNo": "정신건강의학과-2009-001388",
      "year": 2009,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "울산대학교 의과대학",
        "year": 2004,
        "thesis": null
      },
      {
        "degree": "의학박사",
        "school": "울산대학교 대학원",
        "year": 2016,
        "thesis": "초발 정신증의 조기중재 효과"
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "서울아산병원",
        "start_year": 2004,
        "end_year": 2005
      },
      {
        "role": "레지던트",
        "hospital": "서울아산병원 정신건강의학과",
        "start_year": 2005,
        "end_year": 2009
      },
      {
        "role": "전임의",
        "hospital": "서울아산병원 정신건강의학과",
        "start_year": 2009,
        "end_year": 2011
      }
    ],
    "positions": [
      {
        "org": "분당온정신건강의학과병원",
        "title": "병원장",
        "start_year": 2015,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한조현병학회",
        "role": "정회원"
      },
      {
        "name": "대한신경정신의학회",
        "role": "정회원"
      }
    ],
    "publications": [
      {
        "title": "Early intervention in first-episode psychosis",
        "journal": "Psychiatry Investigation",
        "year": 2017,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2012
      }
    ],
    "interests": [
      "초발 정신증",
      "조기중재",
      "급성기 보호병동"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "병원 홈페이지",
        "method": "기관 홈페이지 수집",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy010",
    "name": "임가은",
    "gender": "F",
    "hospitalId": "p7",
    "subspecialty": "강박·외상(PTSD)",
    "reputation": 4.7,
    "reviews": 121,
    "license": {
      "type": "의사면허",
      "no": "제54870호",
      "year": 2008
    },
    "boardCert": {
      "certNo": "정신건강의학과-2016-003055",
      "year": 2016,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "경희대학교 의과대학",
        "year": 2011,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "경희대학교병원",
        "start_year": 2011,
        "end_year": 2012
      },
      {
        "role": "레지던트",
        "hospital": "경희대학교병원 정신건강의학과",
        "start_year": 2012,
        "end_year": 2016
      }
    ],
    "positions": [
      {
        "org": "분당온정신건강의학과병원",
        "title": "과장",
        "start_year": 2018,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한정신건강의학회",
        "role": "회원"
      },
      {
        "name": "한국EMDR협회",
        "role": "회원"
      }
    ],
    "publications": [],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2019
      },
      {
        "name": "EMDR 임상가 인증",
        "year": 2018
      }
    ],
    "interests": [
      "외상후스트레스장애(PTSD)",
      "강박장애",
      "EMDR"
    ],
    "sources": [
      {
        "field": "certifications",
        "source": "한국EMDR협회 인증자 명단",
        "method": "협회 명단 조회",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy011",
    "name": "조은별",
    "gender": "F",
    "hospitalId": "p8",
    "subspecialty": "기분장애(우울/조울)",
    "reputation": 4.5,
    "reviews": 134,
    "license": {
      "type": "의사면허",
      "no": "제52066호",
      "year": 2006
    },
    "boardCert": {
      "certNo": "정신건강의학과-2014-002477",
      "year": 2014,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "인하대학교 의과대학",
        "year": 2009,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "인하대학교병원",
        "start_year": 2009,
        "end_year": 2010
      },
      {
        "role": "레지던트",
        "hospital": "인하대학교병원 정신건강의학과",
        "start_year": 2010,
        "end_year": 2014
      },
      {
        "role": "전임의",
        "hospital": "인하대학교병원 정신건강의학과",
        "start_year": 2014,
        "end_year": 2015
      }
    ],
    "positions": [
      {
        "org": "인천나래정신건강의학과의원",
        "title": "원장",
        "start_year": 2017,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한우울조울병학회",
        "role": "회원"
      }
    ],
    "publications": [],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2017
      }
    ],
    "interests": [
      "우울장애",
      "양극성장애",
      "낮병원 재활"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "의원 홈페이지",
        "method": "기관 홈페이지 수집",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy012",
    "name": "문채원",
    "gender": "F",
    "hospitalId": "p9",
    "subspecialty": "노인정신(치매/섬망)",
    "reputation": 4.4,
    "reviews": 88,
    "license": {
      "type": "의사면허",
      "no": "제49540호",
      "year": 2002
    },
    "boardCert": {
      "certNo": "정신건강의학과-2010-001502",
      "year": 2010,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "건국대학교 의과대학",
        "year": 2005,
        "thesis": null
      },
      {
        "degree": "의학박사",
        "school": "건국대학교 대학원",
        "year": 2017,
        "thesis": "치매 환자의 행동심리증상 관리"
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "건국대학교병원",
        "start_year": 2005,
        "end_year": 2006
      },
      {
        "role": "레지던트",
        "hospital": "건국대학교병원 정신건강의학과",
        "start_year": 2006,
        "end_year": 2010
      }
    ],
    "positions": [
      {
        "org": "고양늘봄정신건강의학과병원",
        "title": "병원장",
        "start_year": 2014,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한노인정신의학회",
        "role": "정회원"
      }
    ],
    "publications": [
      {
        "title": "Management of BPSD in dementia inpatients",
        "journal": "Journal of Korean Geriatric Psychiatry",
        "year": 2018,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2013
      }
    ],
    "interests": [
      "치매 BPSD",
      "노인우울",
      "방문진료"
    ],
    "sources": [
      {
        "field": "publications",
        "source": "KoreaMed",
        "method": "저자명 검색",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy013",
    "name": "배수민",
    "gender": "M",
    "hospitalId": "p10",
    "subspecialty": "정신신체의학",
    "reputation": 4.6,
    "reviews": 119,
    "license": {
      "type": "의사면허",
      "no": "제51745호",
      "year": 2005
    },
    "boardCert": {
      "certNo": "정신건강의학과-2013-002188",
      "year": 2013,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "부산대학교 의과대학",
        "year": 2008,
        "thesis": null
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "분당서울대학교병원",
        "start_year": 2008,
        "end_year": 2009
      },
      {
        "role": "레지던트",
        "hospital": "분당서울대학교병원 정신건강의학과",
        "start_year": 2009,
        "end_year": 2013
      },
      {
        "role": "전임의",
        "hospital": "분당서울대학교병원 정신건강의학과",
        "start_year": 2013,
        "end_year": 2015
      }
    ],
    "positions": [
      {
        "org": "강북힐링정신건강의학과의원",
        "title": "원장",
        "start_year": 2017,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한정신신체의학회",
        "role": "회원"
      }
    ],
    "publications": [],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2016
      }
    ],
    "interests": [
      "화병",
      "스트레스성 신체증상",
      "만성통증 협진"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "의원 홈페이지",
        "method": "기관 홈페이지 수집",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  },
  {
    "id": "psy014",
    "name": "서지안",
    "gender": "F",
    "hospitalId": "p11",
    "subspecialty": "자살예방·정신응급",
    "reputation": 4.7,
    "reviews": 176,
    "license": {
      "type": "의사면허",
      "no": "제48190호",
      "year": 2000
    },
    "boardCert": {
      "certNo": "정신건강의학과-2008-001099",
      "year": 2008,
      "authority": "대한신경정신의학회/보건복지부"
    },
    "education": [
      {
        "degree": "의학사",
        "school": "아주대학교 의과대학",
        "year": 2003,
        "thesis": null
      },
      {
        "degree": "의학박사",
        "school": "아주대학교 대학원",
        "year": 2014,
        "thesis": "응급실 기반 자살예방 사례관리의 효과"
      }
    ],
    "training": [
      {
        "role": "인턴",
        "hospital": "아주대학교병원",
        "start_year": 2003,
        "end_year": 2004
      },
      {
        "role": "레지던트",
        "hospital": "아주대학교병원 정신건강의학과",
        "start_year": 2004,
        "end_year": 2008
      },
      {
        "role": "전임의",
        "hospital": "아주대학교병원 정신건강의학과",
        "start_year": 2008,
        "end_year": 2010
      }
    ],
    "positions": [
      {
        "org": "수원중앙대학교병원 정신건강의학과",
        "title": "교수",
        "start_year": 2012,
        "end_year": null,
        "is_current": 1
      }
    ],
    "societies": [
      {
        "name": "대한신경정신의학회",
        "role": "정회원"
      },
      {
        "name": "한국자살예방협회",
        "role": "이사"
      }
    ],
    "publications": [
      {
        "title": "Effectiveness of ED-based case management for suicide attempters",
        "journal": "Journal of Korean Medical Science",
        "year": 2019,
        "role": "제1저자"
      }
    ],
    "certifications": [
      {
        "name": "정신건강전문의(보건복지부)",
        "year": 2011
      }
    ],
    "interests": [
      "정신응급 협진",
      "자살시도자 사후관리",
      "응급실 정신건강"
    ],
    "sources": [
      {
        "field": "positions",
        "source": "대학병원 의료진 소개",
        "method": "기관 홈페이지 수집",
        "url": null,
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "publications",
        "source": "PubMed",
        "method": "저자명 검색",
        "url": "https://pubmed.ncbi.nlm.nih.gov",
        "collected_at": "2026-06-16",
        "confidence": "medium"
      },
      {
        "field": "boardCert",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      },
      {
        "field": "license",
        "source": "대한신경정신의학회 전문의 명부",
        "method": "학회 명부 정합(probabilistic)",
        "url": "https://www.knpa.or.kr",
        "collected_at": "2026-06-16",
        "confidence": "high"
      }
    ]
  }
];

window.APP_DATA = { SPECIALTIES, HOSPITALS, SPECIALISTS };
