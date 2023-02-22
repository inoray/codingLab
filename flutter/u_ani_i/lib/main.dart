import 'package:flutter/material.dart';
import 'package:u_ani_i/screen/home_screen.dart';

void main() => runApp(
      MaterialApp(
        theme: ThemeData(
          fontFamily: "sunflower",
          textTheme: const TextTheme(
            displayLarge: TextStyle(
              fontSize: 80.0,
              color: Colors.white,
              fontWeight: FontWeight.w700,
              fontFamily: "parisienne",
            ),
            displayMedium: TextStyle(
              color: Colors.white,
              fontSize: 50.0,
              fontWeight: FontWeight.w700,
            ),
            bodyLarge: TextStyle(
              color: Colors.white,
              fontSize: 30.0,
            ),
            bodyMedium: TextStyle(
              color: Colors.white,
              fontSize: 20.0,
            ),
          ),
        ),
        home: const HomeScreen(),
      ),
    );
