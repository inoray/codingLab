using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using WpfApp3.Models;

namespace WpfApp3.ViewModels
{
    public class MainViewModel : ObservableObject
    {
        private MainModel mainModel = new MainModel();
        public MainModel MainModel
        {
            get => mainModel;
            set => SetProperty(ref mainModel, value);
        }

        public RelayCommand ButtonClick { get; }

        public MainViewModel()
        {
            ButtonClick = new RelayCommand(ChangeDigit);
        }

        // 명령 실행 메서드
        private void ChangeDigit()
        {
            MainModel.OutputDigit = MainModel.InputDigit * 2;
        }
    }
}
