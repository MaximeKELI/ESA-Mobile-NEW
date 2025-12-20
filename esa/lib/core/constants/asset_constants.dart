/// Constantes pour les chemins des assets
/// Centralise tous les chemins d'assets pour faciliter leur utilisation
class AssetConstants {
  // Logo de l'école
  static const String logo = 'lib/assets/esalogo.jpeg';
  static const String schoolBuilding = 'lib/assets/school_building.png';
  
  // Icônes de navigation principale
  static const String home = 'lib/assets/home.png';
  static const String profile = 'lib/assets/profile.png';
  static const String message = 'lib/assets/message.png';
  static const String notification = 'lib/assets/notification.png';
  static const String exit = 'lib/assets/exit.png';
  
  // Fonctionnalités académiques
  static const String attendance = 'lib/assets/attendance.png';
  static const String exam = 'lib/assets/exam.png';
  static const String homework = 'lib/assets/homework.png';
  static const String library = 'lib/assets/library.png';
  static const String classroom = 'lib/assets/classroom.png';
  static const String activity = 'lib/assets/activity.png';
  
  // Fonctionnalités administratives
  static const String fee = 'lib/assets/fee.png';
  static const String calendar = 'lib/assets/calendar.png';
  static const String leaveApply = 'lib/assets/leave_apply.png';
  static const String downloads = 'lib/assets/downloads.png';
  
  // Transport
  static const String bus = 'lib/assets/bus.png';
  
  // Animations
  static const String settingGif = 'lib/assets/setting.gif';
  static const String smsAppGif = 'lib/assets/Image&Gif/SMS App.gif';
  static const String schoolSplash = 'lib/assets/school spleash.flr';
  
  // Images illustratives
  static const String img1 = 'lib/assets/Image&Gif/Img_1.PNG';
  static const String img2 = 'lib/assets/Image&Gif/Img_2.PNG';
  static const String img3 = 'lib/assets/Image&Gif/Img_3.PNG';
  static const String img4 = 'lib/assets/Image&Gif/Img_4.PNG';
  static const String img5 = 'lib/assets/Image&Gif/Img_5.PNG';
  static const String img6 = 'lib/assets/Image&Gif/Img_6.PNG';
  static const String img7 = 'lib/assets/Image&Gif/Img_7.PNG';
  static const String img8 = 'lib/assets/Image&Gif/Img_8.PNG';
  
  // Helper pour obtenir une icône par nom
  static String? getIconByName(String name) {
    switch (name.toLowerCase()) {
      case 'home':
        return home;
      case 'profile':
        return profile;
      case 'message':
        return message;
      case 'notification':
        return notification;
      case 'attendance':
        return attendance;
      case 'exam':
        return exam;
      case 'homework':
        return homework;
      case 'library':
        return library;
      case 'fee':
        return fee;
      case 'calendar':
        return calendar;
      case 'bus':
        return bus;
      case 'exit':
        return exit;
      default:
        return null;
    }
  }
}

