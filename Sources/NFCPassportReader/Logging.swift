//
//  Logging.swift
//  NFCTest
//
//  Created by Andy Qua on 11/06/2019.
//  Copyright © 2019 Andy Qua. All rights reserved.
//

import Foundation
import OSLog


extension Logger {
    /// Using your bundle identifier is a great way to ensure a unique identifier.
    private static var subsystem = Bundle.main.bundleIdentifier!
    
    /// Tag Reader logs
    static let passportReader = Log() // Logger(subsystem: subsystem, category: "passportReader")

    /// Tag Reader logs
    static let tagReader = Log() //Logger(subsystem: subsystem, category: "tagReader")

    /// SecureMessaging logs
    static let secureMessaging = Log() //Logger(subsystem: subsystem, category: "secureMessaging")

    static let openSSL = Log() //Logger(subsystem: subsystem, category: "openSSL")

    static let bac = Log() //Logger(subsystem: subsystem, category: "BAC")
    static let chipAuth = Log() //Logger(subsystem: subsystem, category: "chipAuthentication")
    static let pace = Log() //Logger(subsystem: subsystem, category: "PACE")
}

public enum LogLevel : Int, CaseIterable {
	case verbose = 0
	case debug = 1
	case info = 2
	case warning = 3
	case error = 4
	case none = 5
}

public class Log {
    public static var logLevel : LogLevel = .debug
    public static var storeLogs = true
    public static var logData = [String]()
    
    private static let df = DateFormatter()
    private static var dfInit = false

    public class func verbose( _ msg : @autoclosure () -> String ) {
        log( .verbose, msg )
    }
    public class func debug( _ msg : @autoclosure () -> String ) {
        log( .debug, msg )
    }
    public class func info( _ msg : @autoclosure () -> String ) {
        log( .info, msg )
    }
    public class func warning( _ msg : @autoclosure () -> String ) {
        log( .warning, msg )
    }
    public class func error( _ msg : @autoclosure () -> String ) {
        log( .error, msg )
    }
    // philip
	public func verbose( _ msg : @autoclosure () -> String ) {
		Self.log( .verbose, msg )
	}
	public func debug( _ msg : @autoclosure () -> String ) {
		Self.log( .debug, msg )
	}
	public func info( _ msg : @autoclosure () -> String ) {
		Self.log( .info, msg )
	}
	public func warning( _ msg : @autoclosure () -> String ) {
		Self.log( .warning, msg )
	}
	public func error( _ msg : @autoclosure () -> String ) {
		Self.log( .error, msg )
	}
    public class func clearStoredLogs() {
			Self.logData.removeAll()
    }
    
    class func log( _ logLevel : LogLevel, _ msg : () -> String ) {
        guard  logLevel != .none else { return }
        
        if !dfInit {
            df.dateFormat = "y-MM-dd H:m:ss.SSSS"
            dfInit = true
        }
        
        if self.logLevel.rawValue <= logLevel.rawValue {
            let message = msg()
            

            print( "\(df.string(from:Date())) - \(message)" )
            
            if storeLogs {
                logData.append( message )
            }
        }
    }
}
