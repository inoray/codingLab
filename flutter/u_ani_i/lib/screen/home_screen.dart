import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  DateTime firstDay = DateTime.now();

  void onPressed() {
    showCupertinoDialog(
      context: context,
      builder: (BuildContext context) {
        return Align(
          alignment: Alignment.bottomCenter,
          child: Container(
            child: CupertinoDatePicker(
              onDateTimeChanged: (DateTime date) {
                setState(() {
                  firstDay = date;
                });
              },
              mode: CupertinoDatePickerMode.date,
            ),
            height: 300,
            color: Colors.white,
          ),
        );
      },
      barrierDismissible: true,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.pink[100],
      body: SafeArea(
        top: true,
        bottom: false,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _DDay(
                firstDay: firstDay,
                onPressed: onPressed,
              ),
              const _CoupleImage(),
            ],
          ),
        ),
      ),
    );
  }
}

class _DDay extends StatelessWidget {
  final DateTime firstDay;
  final GestureTapCallback onPressed;

  const _DDay({
    Key? key,
    required this.firstDay,
    required this.onPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final DateTime now = DateTime.now();

    return Column(
      children: [
        Text(
          "U&I",
          style: textTheme.displayLarge,
        ),
        Text(
          "우리 처음 만난날",
          style: textTheme.bodyLarge,
        ),
        Text(
          "${firstDay.year}.${firstDay.month}.${firstDay.day}",
          style: textTheme.bodyMedium,
        ),
        IconButton(
          onPressed: () {
            onPressed();
          },
          icon: const Icon(
            Icons.favorite,
            color: Colors.red,
            size: 40.0,
          ),
        ),
        Text(
          "D+${DateTime(now.year, now.month, now.day).difference(firstDay).inDays + 1}",
          style: textTheme.displayMedium,
        ),
      ],
    );
  }
}

class _CoupleImage extends StatelessWidget {
  const _CoupleImage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Image.asset(
        "asset/img/middle_image.png",
        height: MediaQuery.of(context).size.height / 2,
      ),
    );
  }
}
