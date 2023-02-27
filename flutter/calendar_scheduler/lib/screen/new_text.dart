import 'package:flutter/material.dart';

class MyText extends StatelessWidget {
  const MyText({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '의지',
              style: TextStyle(
                fontSize: 60.0,
                fontWeight: FontWeight.w700,
                color: Colors.red
              ),
            ),
            Text(
              '용기',
              style: TextStyle(
                  fontSize: 60.0,
                  fontWeight: FontWeight.w700,
                  color: Colors.orange,
              ),
            ),
            Text(
              '정의',
              style: TextStyle(
                fontSize: 60.0,
                fontWeight: FontWeight.w700,
                color: Colors.yellow
              ),
            ),
            Text(
              '친절',
              style: TextStyle(
                  fontSize: 60.0,
                  fontWeight: FontWeight.w700,
                  color: Colors.green,
              ),
            ),
            Text(
              '인내',
              style: TextStyle(
                fontSize: 60.0,
                fontWeight: FontWeight.w700,
                color: Colors.cyan,
              ),
            ),
            Text(
              '고결',
              style: TextStyle(
                fontSize: 60.0,
                fontWeight: FontWeight.w700,
                color: Colors.blue,
              ),
            ),
            Text(
              '끈기',
              style: TextStyle(
                fontSize: 60.0,
                fontWeight: FontWeight.w700,
                color: Colors.purple,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
