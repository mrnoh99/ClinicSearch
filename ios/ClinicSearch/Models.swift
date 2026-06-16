import Foundation
import CoreLocation

/// 의료진
struct Doctor: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let title: String          // 직위 (교수/원장/과장)
    let specialty: String      // 전문과목
    let subspecialty: String   // 세부전공
    let school: String         // 졸업학교
    let gradYear: Int          // 졸업연도
    let training: String       // 수련병원
    let career: [String]       // 경력
    let reputation: Double      // 평판 0~5
    let reviews: Int           // 후기 수
}

/// 병원
struct Hospital: Identifiable, Hashable {
    let id: String
    let name: String
    let type: String
    let address: String
    let lat: Double
    let lng: Double
    let phone: String
    let beds: Int
    let er: Bool               // 응급실 운영
    let erLevel: String?       // 응급의료기관 등급
    let icu: Bool              // 중환자실
    let parking: Bool
    let transit: String
    let ambulanceBay: Bool     // 구급차 전용 진입로
    let transferDesk: Bool     // 전원 전담 코디네이터
    let avgWaitMin: Int
    let specialties: [String]
    let doctors: [Doctor]

    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: lat, longitude: lng)
    }
}

/// 검색 결과(거리·점수 포함)
struct ScoredHospital: Identifiable {
    let hospital: Hospital
    let distanceKm: Double
    let driveMin: Int
    let score: Int
    var id: String { hospital.id }
}

/// 정렬 기준
enum SortMode: String, CaseIterable, Identifiable {
    case score = "전원 적합도순"
    case distance = "거리순"
    var id: String { rawValue }
}
