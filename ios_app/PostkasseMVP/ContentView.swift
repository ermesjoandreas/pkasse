import SwiftUI

struct ContentView: View {
    @StateObject private var networkManager = NetworkManager()
    @State private var inputImage: UIImage?
    @State private var showingCamera = false
    @State private var results: [PostkasseResult] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    // Custom camera trigger
    private let cameraCoordinator = ARCameraCoordinatorHolder()
     
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
                        Image(systemName: "camera.viewfinder")
                        Text("Start Live Kamera")
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
            .navigationTitle("Postkasse Vision AR")
            .sheet(isPresented: $showingCamera, onDismiss: analyzeImage) {
                // Custom AR Camera Overlay
                ZStack(alignment: .bottom) {
                    ARCameraView(image: $inputImage, isPresented: $showingCamera)
                        .edgesIgnoringSafeArea(.all)
                        .environmentObject(cameraCoordinator) 
                        
                    // Shutter Button OVER the camera view
                    Button(action: {
                        cameraCoordinator.triggerAction?()
                    }) {
                        Circle()
                            .fill(Color.white)
                            .frame(width: 70, height: 70)
                            .overlay(Circle().stroke(Color.black, lineWidth: 2))
                            .shadow(radius: 10)
                    }
                    .padding(.bottom, 50)
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

// Helper to bridge the Action from View to Coordinator
class ARCameraCoordinatorHolder: ObservableObject {
    var triggerAction: (() -> Void)?
}

// Need to update ARCameraView to accept the holder
extension ARCameraView {
    func makeCoordinator() -> Coordinator {
        let coord = Coordinator(self)
        // This is a bit hacky for MVP but works: 
        // We need to pass the trigger function up to the holder
        // But we access holder via EnvironmentObject inside View, harder in init.
        // Simplified: The View body below binds it.
        return coord
    }
    
    // We modify ARCameraView struct to take the env object
}

// Re-defining ARCameraView wrapper to include the injection logic clearly
struct ARCameraViewWrapper: View {
    @Binding var image: UIImage?
    @Binding var isPresented: Bool
    @EnvironmentObject var coordinatorHolder: ARCameraCoordinatorHolder
    
    var body: some View {
        ARCameraViewInitial(image: $image, isPresented: $isPresented, holder: coordinatorHolder)
    }
}

// Inner struct for Representable
struct ARCameraViewInitial: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Binding var isPresented: Bool
    var holder: ARCameraCoordinatorHolder
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    func makeUIViewController(context: Context) -> CameraViewController {
        let controller = CameraViewController()
        controller.delegate = context.coordinator
        context.coordinator.controller = controller
        
        // Bind the trigger action!
        holder.triggerAction = {
            controller.capturePhoto()
        }
        
        return controller
    }
    
    func updateUIViewController(_ uiViewController: CameraViewController, context: Context) {}
    
    class Coordinator: NSObject, CameraViewControllerDelegate {
        var parent: ARCameraViewInitial
        var controller: CameraViewController?
        
        init(_ parent: ARCameraViewInitial) {
            self.parent = parent
        }
        
        func didCaptureImage(_ image: UIImage) {
            parent.image = image
            parent.isPresented = false
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
