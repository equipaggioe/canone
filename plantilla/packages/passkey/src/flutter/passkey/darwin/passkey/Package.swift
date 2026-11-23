// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "passkey",
    platforms: [
        // Passkeys that sync came with iOS 16; the API is on macOS since 12.
        .iOS("16.0"),
        .macOS("12.0"),
    ],
    products: [
        .library(name: "passkey", targets: ["passkey"])
    ],
    dependencies: [
        .package(name: "FlutterFramework", path: "../FlutterFramework")
    ],
    targets: [
        .target(
            name: "passkey",
            dependencies: [
                .product(name: "FlutterFramework", package: "FlutterFramework")
            ]
        )
    ]
)
