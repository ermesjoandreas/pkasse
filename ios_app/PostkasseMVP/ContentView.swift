import SwiftUI

struct ContentView: View {
    @StateObject private var networkManager = NetworkManager()
    @State private var inputImage: UIImage?
    @State private var showingCamera = false
    @State private var results: [PostkasseResult] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            VStack {
                if let inputImage = inputImage {
                    Image(uiImage: inputImage)
                        .resizable()
                        .scaledToFit()
                        .frame(height: 200)
                        .cornerRadius(10)
                        .padding()
                } else {
                    Rectangle()
                        .fill(Color.secondary.opacity(0.1))
                        .frame(height: 200)
                        .overlay(Text("Ta bilde for å starte"))
                        .padding()
                }
                
                if isLoading {
                    ProgressView("Analyserer (Sender til Python)...")
                } else if let error = errorMessage {
                    Text("Feil: \(error)")
                        .foregroundColor(.red)
                        .font(.caption)
                }
                
                List(results) { pk in
                    HStack {
                        VStack(alignment: .leading) {
                            Text(pk.id)
                                .font(.headline)
                            Text("Kapasitet")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        BadgeView(text: pk.kapasitetKlasse)
                    }
                }
                .listStyle(PlainListStyle())
                
                Spacer()
                
                Button(action: {
                    showingCamera = true
                }) {
                    HStack {
                        Image(systemName: "camera.fill")
                        Text("Ta Bilde")
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.blue)
                    .cornerRadius(12)
                }
                .padding()
            }
            .navigationTitle("Postkasse Vision")
            .sheet(isPresented: $showingCamera, onDismiss: analyzeImage) {
                CameraView(image: $inputImage)
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    // Quick server IP config (simplified for MVP)
                    Button(action: {
                        // In real app, open settings
                        // here just toggle localhost vs a typical IP for demo example
                        if networkManager.serverURL.contains("localhost") {
                            // Example of hardcoded fallback or prompting user would go here
                            // For now just print to console
                            print("Server URL is: \(networkManager.serverURL)")
                        }
                    }) {
                        Image(systemName: "network")
                    }
                }
            }
        }
    }
    
    func analyzeImage() {
        guard let inputImage = inputImage else { return }
        
        isLoading = true
        errorMessage = nil
        results = [] // Clear previous
        
        Task {
            do {
                let foundPostkasser = try await networkManager.uploadImage(image: inputImage)
                DispatchQueue.main.async {
                    self.results = foundPostkasser
                    self.isLoading = false
                }
            } catch {
                DispatchQueue.main.async {
                    self.errorMessage = error.localizedDescription
                    self.isLoading = false
                }
            }
        }
    }
}

struct BadgeView: View {
    let text: String
    
    var color: Color {
        switch text {
        case "STOR": return .green
        case "STANDARD": return .blue
        case "LITEN": return .orange
        default: return .gray
        }
    }
    
    var body: some View {
        Text(text)
            .font(.caption)
            .fontWeight(.bold)
            .padding(6)
            .background(color.opacity(0.2))
            .foregroundColor(color)
            .cornerRadius(8)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
