import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  DateTime firstDay = DateTime.now();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.pink[100],
      body: const SafeArea(
        top: true,
        bottom: false,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _DDay(),
              _CoupleImage(),
            ],
          ),
        ),
      ),
    );
  }
}

class _DDay extends StatelessWidget {
  const _DDay({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

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
          "2022.11.28",
          style: textTheme.bodyMedium,
        ),
        IconButton(
          onPressed: () {},
          icon: const Icon(
            Icons.favorite,
            color: Colors.red,
            size: 40.0,
          ),
        ),
        Text(
          "D+365",
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
