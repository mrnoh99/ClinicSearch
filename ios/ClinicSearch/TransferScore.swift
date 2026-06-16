import Foundation
import CoreLocation

/// 거리 및 전원 적합도 계산 (웹앱 js/app.js 로직과 동일)
enum TransferScore {

    /// 두 좌표 사이 직선거리(km) — Haversine
    static func haversineKm(_ a: CLLocationCoordinate2D, _ b: CLLocationCoordinate2D) -> Double {
        let r = 6371.0
        let dLat = (b.latitude - a.latitude) * .pi / 180
        let dLng = (b.longitude - a.longitude) * .pi / 180
        let lat1 = a.latitude * .pi / 180
        let lat2 = b.latitude * .pi / 180
        let h = pow(sin(dLat / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(dLng / 2), 2)
        return 2 * r * asin(min(1, sqrt(h)))
    }

    /// 도심 평균속도(28km/h) 기준 예상 이동시간(분)
    static func driveMinutes(_ km: Double) -> Int {
        Int((km / 28.0 * 60).rounded())
    }

    /// 전원 적합도 점수 (0~100)
    /// 거리(45) + 응급/중환자 인프라(25) + 접근성(18) + 대기시간(12)
    static func score(for h: Hospital, distanceKm km: Double) -> Int {
        // 거리: 0km=45점, 30km=0점
        let distScore = max(0, 45 * (1 - min(km, 30) / 30))

        // 인프라
        var infra = 0.0
        if h.er { infra += 10 }
        if h.erLevel == "권역응급의료센터" { infra += 6 }
        else if h.erLevel == "지역응급의료센터" { infra += 3 }
        if h.icu { infra += 9 }
        infra = min(infra, 25)

        // 접근성
        var access = 0.0
        if h.ambulanceBay { access += 6 }
        if h.transferDesk { access += 6 }
        if h.parking { access += 3 }
        if !h.transit.isEmpty { access += 3 }
        access = min(access, 18)

        // 대기시간: 10분 이하 만점, 60분 이상 0점
        let cappedWait = Double(min(max(h.avgWaitMin - 10, 0), 50))
        let waitScore = max(0, 12 * (1 - cappedWait / 50))

        return Int((distScore + infra + access + waitScore).rounded())
    }

    /// 필터·정렬 적용한 결과 생성
    static func search(
        hospitals: [Hospital],
        origin: CLLocationCoordinate2D,
        specialty: String?,
        subspecialty: String?,
        requireER: Bool,
        requireICU: Bool,
        maxKm: Double,
        sort: SortMode
    ) -> [ScoredHospital] {
        var results = hospitals.compactMap { h -> ScoredHospital? in
            if let s = specialty, !s.isEmpty, !h.specialties.contains(s) { return nil }
            if let sub = subspecialty, !sub.isEmpty,
               !h.doctors.contains(where: { $0.subspecialty == sub }) { return nil }
            if requireER && !h.er { return nil }
            if requireICU && !h.icu { return nil }

            let km = haversineKm(origin, h.coordinate)
            if maxKm > 0 && km > maxKm { return nil }
            return ScoredHospital(hospital: h, distanceKm: km,
                                  driveMin: driveMinutes(km),
                                  score: score(for: h, distanceKm: km))
        }

        switch sort {
        case .distance:
            results.sort { $0.distanceKm < $1.distanceKm }
        case .score:
            results.sort { $0.score != $1.score ? $0.score > $1.score : $0.distanceKm < $1.distanceKm }
        }
        return results
    }
}
