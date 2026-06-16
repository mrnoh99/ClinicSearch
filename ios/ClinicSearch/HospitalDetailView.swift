import SwiftUI
import MapKit

struct HospitalDetailView: View {
    let scored: ScoredHospital
    let origin: CLLocationCoordinate2D?
    @Environment(\.dismiss) private var dismiss

    private var h: Hospital { scored.hospital }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    facts
                    transferBox
                    actions
                    Divider()
                    Text("의료진 (\(h.doctors.count)명)").font(.headline)
                    ForEach(h.doctors) { DoctorCard(doctor: $0) }
                }
                .padding()
            }
            .navigationTitle(h.name)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("닫기") { dismiss() }
                }
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(h.type).font(.subheadline).foregroundStyle(.secondary)
            Text(h.address).font(.subheadline)
        }
    }

    private var facts: some View {
        LazyVGrid(columns: [GridItem(.flexible(), alignment: .leading),
                            GridItem(.flexible(), alignment: .leading)], spacing: 10) {
            fact("거리", String(format: "%.1f km · 약 %d분", scored.distanceKm, scored.driveMin))
            fact("병상", "\(h.beds)병상")
            fact("응급", h.er ? (h.erLevel ?? "응급실 운영") : "응급실 없음")
            fact("중환자실", h.icu ? "운영" : "없음")
            fact("교통", h.transit)
            fact("주차", h.parking ? "가능" : "불가")
        }
    }

    private func fact(_ label: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 1) {
            Text(label).font(.caption2).foregroundStyle(.secondary)
            Text(value).font(.subheadline)
        }
    }

    private var transferBox: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("전원 접근성").font(.caption.bold()).foregroundStyle(.secondary)
            HStack {
                if h.ambulanceBay { chip("구급차 전용 진입로", .green) }
                if h.transferDesk { chip("전원 전담 코디네이터", .green) }
                chip("적합도 \(scored.score)점", .orange)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var actions: some View {
        HStack {
            Button {
                openDirections()
            } label: {
                Label("길찾기", systemImage: "car.fill").frame(maxWidth: .infinity)
            }.buttonStyle(.borderedProminent)

            Button {
                if let url = URL(string: "tel://\(h.phone.replacingOccurrences(of: "-", with: ""))") {
                    UIApplication.shared.open(url)
                }
            } label: {
                Label("전화", systemImage: "phone.fill").frame(maxWidth: .infinity)
            }.buttonStyle(.bordered)
        }
    }

    private func openDirections() {
        let place = MKMapItem(placemark: MKPlacemark(coordinate: h.coordinate))
        place.name = h.name
        place.openInMaps(launchOptions: [MKLaunchOptionsDirectionsModeKey: MKLaunchOptionsDirectionsModeDriving])
    }

    private func chip(_ t: String, _ c: Color) -> some View {
        Text(t).font(.caption2.bold())
            .padding(.horizontal, 8).padding(.vertical, 4)
            .background(c.opacity(0.15)).foregroundStyle(c)
            .clipShape(Capsule())
    }
}

// MARK: - 의료진 카드
struct DoctorCard: View {
    let doctor: Doctor

    private var initials: String { String(doctor.name.suffix(2)) }
    private var avatarColor: Color {
        let palette: [Color] = [.blue, .teal, .purple, .pink, .orange, .indigo, .green]
        let idx = abs(doctor.name.hashValue) % palette.count
        return palette[idx]
    }

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            ZStack {
                RoundedRectangle(cornerRadius: 12).fill(avatarColor)
                Text(initials).foregroundStyle(.white).font(.title3.bold())
            }
            .frame(width: 64, height: 64)

            VStack(alignment: .leading, spacing: 3) {
                HStack {
                    Text(doctor.name).font(.headline)
                    Text(doctor.title).font(.caption).foregroundStyle(.secondary)
                }
                Text("\(doctor.specialty) · \(doctor.subspecialty)")
                    .font(.subheadline).foregroundStyle(.teal)
                HStack(spacing: 2) {
                    ForEach(0..<5) { i in
                        Image(systemName: i < Int(doctor.reputation.rounded()) ? "star.fill" : "star")
                            .font(.caption2).foregroundStyle(.orange)
                    }
                    Text(String(format: "%.1f (%d건)", doctor.reputation, doctor.reviews))
                        .font(.caption2).foregroundStyle(.secondary)
                }
                Text("🎓 \(doctor.school) (\(String(doctor.gradYear))년 졸업)")
                    .font(.caption).foregroundStyle(.secondary)
                Text("🏥 수련: \(doctor.training)")
                    .font(.caption).foregroundStyle(.secondary)
                ForEach(doctor.career, id: \.self) { c in
                    Text("• \(c)").font(.caption).foregroundStyle(.secondary)
                }
            }
            Spacer()
        }
        .padding(.vertical, 6)
    }
}
