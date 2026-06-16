import Foundation
import CoreLocation

/// 현재 위치 권한 요청 및 좌표 제공
@MainActor
final class LocationManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    @Published var coordinate: CLLocationCoordinate2D?
    @Published var statusMessage: String = ""

    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
    }

    func requestLocation() {
        statusMessage = "현재 위치를 확인하는 중..."
        switch manager.authorizationStatus {
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        case .denied, .restricted:
            statusMessage = "위치 권한이 거부되었습니다. 설정에서 허용하거나 주소를 입력하세요."
        default:
            manager.requestLocation()
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        let status = m.authorizationStatus
        Task { @MainActor in
            if status == .authorizedWhenInUse || status == .authorizedAlways {
                m.requestLocation()
            } else if status == .denied || status == .restricted {
                statusMessage = "위치 권한이 거부되었습니다."
            }
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let loc = locations.last else { return }
        Task { @MainActor in
            coordinate = loc.coordinate
            statusMessage = "현재 위치를 기준으로 설정했습니다."
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in
            statusMessage = "위치를 가져오지 못했습니다: \(error.localizedDescription)"
        }
    }
}

/// 주소 → 좌표 (CLGeocoder 사용, 별도 API 키 불필요)
enum Geocoder {
    static func geocode(_ address: String) async throws -> (CLLocationCoordinate2D, String) {
        let placemarks = try await CLGeocoder().geocodeAddressString(address)
        guard let p = placemarks.first, let loc = p.location else {
            throw NSError(domain: "Geocoder", code: 404,
                          userInfo: [NSLocalizedDescriptionKey: "주소를 찾을 수 없습니다"])
        }
        let label = [p.locality, p.thoroughfare, p.subThoroughfare]
            .compactMap { $0 }.joined(separator: " ")
        return (loc.coordinate, label.isEmpty ? address : label)
    }
}
