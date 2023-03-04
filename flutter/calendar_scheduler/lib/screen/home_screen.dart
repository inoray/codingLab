import 'package:flutter/material.dart';
import 'package:calendar_scheduler/component/main_calendar.dart';
import 'package:calendar_scheduler/component/schedule_card.dart';
import 'package:calendar_scheduler/component/today_banner.dart';
import 'package:calendar_scheduler/component/schedule_bottom_sheet.dart';
import 'package:calendar_scheduler/const/colors.dart';
import 'package:get_it/get_it.dart';
import 'package:calendar_scheduler/database/drift_database.dart';
import 'package:calendar_scheduler/provider/schedule_provider.dart';
import 'package:provider/provider.dart';

// class HomeScreen extends StatefulWidget {
//   const HomeScreen({Key? key}) : super(key: key);
//
//   @override
//   State<HomeScreen> createState() => _HomeScreenState();
// }

class HomeScreen extends StatelessWidget {
  DateTime selectedDate = DateTime.utc(
    DateTime.now().year,
    DateTime.now().month,
    DateTime.now().day,
  );

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ScheduleProvider>();
    final selectedDate = provider.selectedDate;
    final schdules = provider.cache[selectedDate] ?? [];

    return Scaffold(
      floatingActionButton: FloatingActionButton(
        backgroundColor: PRIMARY_COLOR,
        onPressed: () {
          showModalBottomSheet(
            context: context,
            builder: (_) => ScheduleBottomSheet(
              selectedDate: selectedDate,
            ),
            isDismissible: true,
            isScrollControlled: true,
          );
        },
        child: const Icon(
          Icons.add,
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            MainCalendar(
              selectedDate: selectedDate,
              onDaySelected: (selectedDate, focusedDate) =>
                  onDaySelected(selectedDate, focusedDate, context),
            ),
            const SizedBox(height: 8.0),
            // StreamBuilder(
            //   stream: GetIt.I<LocalDatabase>().watchSchedule(selectedDate),
            //   builder: (context, snapshot) {
            //     return TodayBanner(
            //       selectedDate: selectedDate,
            //       count: snapshot.data!.length ?? 0,
            //     );
            //   },
            // ),
            TodayBanner(
              selectedDate: selectedDate,
              count: schdules.length,
            ),
            const SizedBox(height: 8.0),
            // Expanded(
            //   child: StreamBuilder<List<Schedule>>(
            //     stream: GetIt.I<LocalDatabase>().watchSchedule(selectedDate),
            //     builder: (context, snapshot) {
            //       if (!snapshot.hasData) {
            //         return Container();
            //       }
            //
            //       return ListView.builder(
            //         itemCount: snapshot.data!.length,
            //         itemBuilder: (context, index) {
            //           final schedule = snapshot.data![index];
            //
            //           return Dismissible(
            //             key: ObjectKey(schedule.id),
            //             direction: DismissDirection.startToEnd,
            //             onDismissed: (DismissDirection direction) {
            //               GetIt.I<LocalDatabase>().removeSchedule(schedule.id);
            //             },
            //             child: Padding(
            //               padding: const EdgeInsets.only(
            //                   bottom: 8.0, left: 8.0, right: 8.0),
            //               child: ScheduleCard(
            //                 startTime: schedule.startTime,
            //                 endTime: schedule.endTime,
            //                 content: schedule.content,
            //               ),
            //             ),
            //           );
            //         },
            //       );
            //     },
            //   ),
            // ),
            Expanded(
              child: ListView.builder(
                itemCount: schdules.length,
                itemBuilder: (context, index) {
                  final schedule = schdules[index];

                  return Dismissible(
                    key: ObjectKey(schedule.id),
                    direction: DismissDirection.startToEnd,
                    onDismissed: (DismissDirection direction) {
                      provider.deleteSchedule(
                          date: selectedDate, id: schedule.id);
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(
                          bottom: 8.0, left: 8.0, right: 8.0),
                      child: ScheduleCard(
                        startTime: schedule.startTime,
                        endTime: schedule.endTime,
                        content: schedule.content,
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  void onDaySelected(
    DateTime selectedDate,
    DateTime focusedDate,
    BuildContext context,
  ) {
    // setState(() {
    //   this.selectedDate = selectedDate;
    // });
    final provider = context.read<ScheduleProvider>();
    provider.changeSelectedDate(
      date: selectedDate,
    );
    provider.getSchedules(
      date: selectedDate,
    );
  }
}
