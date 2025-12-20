import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/app_theme_enhanced.dart';
import 'core/services/api_service.dart';
import 'core/services/auth_service.dart';
import 'core/routes/app_router.dart';
import 'core/navigation/navigation_service.dart';
import 'screens/auth/login_screen.dart';
import 'screens/home/home_screen.dart';
import 'providers/auth_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialiser les services
  await ApiService().init();
  await AuthService().init();
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: MaterialApp(
        title: 'ESA - Gestion Scolaire',
        debugShowCheckedModeBanner: false,
        theme: AppThemeEnhanced.lightTheme,
        darkTheme: AppThemeEnhanced.darkTheme,
        themeMode: ThemeMode.light,
        navigatorKey: NavigationService().navigatorKey,
        home: const AuthWrapper(),
        onGenerateRoute: (settings) => AppRoutes.generateRoute(settings),
        // Transitions personnalisées
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.android: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
            TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.macOS: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
          },
        ),
      ),
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    // Recharger l'utilisateur au démarrage
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<AuthProvider>(context, listen: false).reloadUser();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, _) {
        if (authProvider.isLoading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        
        if (authProvider.isAuthenticated && authProvider.user != null) {
          return const HomeScreen();
        }
        
        return const LoginScreen();
      },
    );
  }
}
