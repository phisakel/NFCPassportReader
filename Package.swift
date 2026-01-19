// swift-tools-version:5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "NFCPassportReader",
    platforms: [.iOS(.v15), .macOS(.v12)],
    products: [
        // Products define the executables and libraries produced by a package, and make them visible to other packages.
        .library(
            name: "NFCPassportReader",
            targets: ["NFCPassportReader", "OpenSSL"]),
    ],
    dependencies: [
        // Dependencies declare other packages that this package depends on.
        // .package(url: /* package url */, from: "1.0.0"),
        // dont use source -->  .package(url: "https://github.com/krzyzanowskim/OpenSSL.git", .upToNextMinor(from: "1.1.2300"))
    ],
    targets: [
        // Targets are the basic building blocks of a package. A target can define a module or a test suite.
        // Targets can depend on other targets in this package, and on products in packages which this package depends on.
        .target(
            name: "NFCPassportReader",
            dependencies: [.target(name: "OpenSSL")]),
		.binaryTarget(name: "OpenSSL", path: "./OpenSSL.xcframework"),
        .testTarget(
            name: "NFCPassportReaderTests",
            dependencies: ["NFCPassportReader"]),
    ]
)

