import SwiftUI
import MapKit

struct ContentView: View {
    @StateObject private var location = LocationManager()

    @State private var address = ""
    @State private var origin: CLLocationCoordinate2D?
    @State private var originLabel = ""
    @State private var specialty = ""
    @State private var subspecialty = ""
    @State private var requireER = false
    @State private var requireICU = false
    @State private var maxKm: Double = 0
    @State private var sort: SortMode = .score
    @State private var results: [ScoredHospital] = []
    @State private var selected: ScoredHospital?
    @State private var status = "거주지 주소를 입력하거나 현재 위치를 사용하세요."
    @State private var camera: MapCameraPosition = .region(
        MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 37.5665, longitude: 126.978),
                           span: MKCoordinateSpan(latitudeDelta: 0.4, longitudeDelta: 0.4)))

    private var subOptions: [String] {
        SPECIALTIES.first(where: { $0.name == specialty })?.subs ?? []
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                searchBar
                map
                resultsList
            }
            .navigationTitle("전원 병원 찾기")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(item: $selected) { HospitalDetailView(scored: $0, origin: origin) }
            .onChange(of: location.coordinate) { _, new in
                if let c = new { origin = c; originLabel = "현재 위치"; address = "현재 위치 (GPS)"; runSearch() }
            }
            .onChange(of: location.statusMessage) { _, m in if !m.isEmpty { status = m } }
        }
    }

    // MARK: 검색 바
    private var searchBar: some View {
        VStack(spacing: 10) {
            HStack {
                TextField("거주지 주소 (예: 서울시 강남구 테헤란로 415)", text: $address)
                    .textFieldStyle(.roundedBorder)
                    .submitLabel(.search)
                    .onSubmit { Task { await geocodeAddress() } }
                Button("검색") { Task { await geocodeAddress() } }
                    .buttonStyle(.borderedProminent)
            }
            Button {
                location.requestLocation()
            } label: {
                Label("현재 위치 사용", systemImage: "location.fill")
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            HStack {
                Picker("전문과목", selection: $specialty) {
                    Text("전체 전문과목").tag("")
                    ForEach(SPECIALTIES, id: \.name) { Text($0.name).tag($0.name) }
                }
                Picker("세부전공", selection: $subspecialty) {
                    Text("세부전공 전체").tag("")
                    ForEach(subOptions, id: \.self) { Text($0).tag($0) }
                }
                .disabled(subOptions.isEmpty)
            }
            .pickerStyle(.menu)
            .onChange(of: specialty) { _, _ in subspecialty = ""; runSearch() }
            .onChange(of: subspecialty) { _, _ in runSearch() }

            HStack {
                Picker("정렬", selection: $sort) {
                    ForEach(SortMode.allCases) { Text($0.rawValue).tag($0) }
                }.pickerStyle(.segmented)
            }
            .onChange(of: sort) { _, _ in runSearch() }

            HStack(spacing: 16) {
                Toggle("응급실", isOn: $requireER).fixedSize()
                Toggle("중환자실", isOn: $requireICU).fixedSize()
                Spacer()
            }
            .toggleStyle(.button)
            .onChange(of: requireER) { _, _ in runSearch() }
            .onChange(of: requireICU) { _, _ in runSearch() }

            Text(status).font(.footnote).foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding()
        .background(.thinMaterial)
    }

    // MARK: 지도
    private var map: some View {
        Map(position: $camera) {
            if let o = origin {
                Annotation("기준 위치", coordinate: o) {
                    Image(systemName: "house.circle.fill")
                        .font(.title).foregroundStyle(.teal)
                }
            }
            ForEach(Array(results.enumerated()), id: \.element.id) { idx, r in
                Annotation("\(idx + 1)", coordinate: r.hospital.coordinate) {
                    ZStack {
                        Circle().fill(idx == 0 ? .orange : .blue)
                            .frame(width: 28, height: 28)
                        Text("\(idx + 1)").foregroundStyle(.white).font(.caption.bold())
                    }
                    .onTapGesture { selected = r }
                }
            }
        }
        .frame(height: 300)
    }

    // MARK: 결과 리스트
    private var resultsList: some View {
        List {
            Section("검색 결과 \(results.count)곳") {
                ForEach(Array(results.enumerated()), id: \.element.id) { idx, r in
                    Button { selected = r } label: { ResultRow(index: idx, scored: r) }
                        .buttonStyle(.plain)
                }
                if results.isEmpty {
                    Text("조건에 맞는 병원이 없습니다.").foregroundStyle(.secondary)
                }
            }
        }
        .listStyle(.plain)
    }

    // MARK: 동작
    private func geocodeAddress() async {
        let q = address.trimmingCharacters(in: .whitespaces)
        guard !q.isEmpty, q != "현재 위치 (GPS)" else { status = "거주지 주소를 입력하세요."; return }
        status = "주소를 검색하는 중..."
        do {
            let (coord, label) = try await Geocoder.geocode(q)
            origin = coord; originLabel = label
            runSearch()
        } catch {
            status = "주소 검색 실패: \(error.localizedDescription)"
        }
    }

    private func runSearch() {
        guard let o = origin else { status = "먼저 위치를 설정하세요."; return }
        results = TransferScore.search(hospitals: HOSPITALS, origin: o,
                                       specialty: specialty, subspecialty: subspecialty,
                                       requireER: requireER, requireICU: requireICU,
                                       maxKm: maxKm, sort: sort)
        status = results.isEmpty ? "조건에 맞는 병원이 없습니다." :
            "\(originLabel) 기준 \(results.count)개 병원을 찾았습니다."
        fitCamera(origin: o)
    }

    private func fitCamera(origin o: CLLocationCoordinate2D) {
        var lats = [o.latitude], lngs = [o.longitude]
        results.prefix(8).forEach { lats.append($0.hospital.lat); lngs.append($0.hospital.lng) }
        guard let minLat = lats.min(), let maxLat = lats.max(),
              let minLng = lngs.min(), let maxLng = lngs.max() else { return }
        let center = CLLocationCoordinate2D(latitude: (minLat + maxLat) / 2,
                                            longitude: (minLng + maxLng) / 2)
        let span = MKCoordinateSpan(latitudeDelta: max((maxLat - minLat) * 1.4, 0.03),
                                    longitudeDelta: max((maxLng - minLng) * 1.4, 0.03))
        withAnimation { camera = .region(MKCoordinateRegion(center: center, span: span)) }
    }
}

// MARK: - 결과 행
struct ResultRow: View {
    let index: Int
    let scored: ScoredHospital
    var h: Hospital { scored.hospital }

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            VStack {
                Text("#\(index + 1)").font(.caption2).foregroundStyle(.secondary)
                Text("\(scored.score)").font(.title3.bold()).foregroundStyle(.teal)
                Text("점").font(.caption2).foregroundStyle(.secondary)
            }
            .frame(width: 44)

            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(h.name).font(.headline)
                    if index == 0 {
                        Text("최적 전원지").font(.caption2.bold())
                            .padding(.horizontal, 6).padding(.vertical, 2)
                            .background(.orange.opacity(0.2)).foregroundStyle(.orange)
                            .clipShape(Capsule())
                    }
                }
                Text(h.type).font(.caption).foregroundStyle(.secondary)
                HStack(spacing: 10) {
                    Label(String(format: "%.1f km", scored.distanceKm), systemImage: "mappin")
                    Label("약 \(scored.driveMin)분", systemImage: "car.fill")
                    Label("\(h.beds)병상", systemImage: "bed.double.fill")
                }
                .font(.caption2).foregroundStyle(.secondary)
                HStack(spacing: 6) {
                    if h.psychER { tag("정신응급", .red) }
                    if h.closedWard { tag("보호병동", .purple) }
                    if h.inpatient { tag("입원가능", .blue) }
                    if h.dayHospital { tag("낮병원", .green) }
                }
            }
            Spacer()
        }
        .padding(.vertical, 4)
    }

    private func tag(_ t: String, _ c: Color) -> some View {
        Text(t).font(.caption2.bold())
            .padding(.horizontal, 6).padding(.vertical, 2)
            .background(c.opacity(0.15)).foregroundStyle(c)
            .clipShape(Capsule())
    }
}
