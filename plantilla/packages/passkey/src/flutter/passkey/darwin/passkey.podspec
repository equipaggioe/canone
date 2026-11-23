Pod::Spec.new do |s|
  s.name             = 'passkey'
  s.version          = '0.1.0'
  s.summary          = 'The passkeys of iOS and macOS, with AuthenticationServices.'
  s.homepage         = 'https://github.com/'
  s.license          = { :type => 'Proprietary' }
  s.author           = 'canone'
  s.source           = { :path => '.' }
  s.source_files     = 'passkey/Sources/passkey/**/*'
  s.ios.dependency 'Flutter'
  s.osx.dependency 'FlutterMacOS'
  s.ios.deployment_target = '16.0'
  s.osx.deployment_target = '12.0'
  s.pod_target_xcconfig = { 'DEFINES_MODULE' => 'YES', 'EXCLUDED_ARCHS[sdk=iphonesimulator*]' => 'i386' }
  s.swift_version = '5.0'
end
