// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "passkey",
    platforms: [
        // Passkeys that sync came with iOS 16 and macOS 13.
        .iOS("16.0"),
        .macOS("13.0"),
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
