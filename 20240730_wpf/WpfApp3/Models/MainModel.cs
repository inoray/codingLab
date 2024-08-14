using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WpfApp3.Models
{
    public class MainModel : ObservableObject
    {
        private int inputDigit;
        public int InputDigit
        {
            get => inputDigit;
            set
            {
                //OutputDigit = value * 2;
                SetProperty(ref inputDigit, value);
            }
        }

        private int outputDigit;
        public int OutputDigit
        {
            get => outputDigit;
            set => SetProperty(ref outputDigit, value);
        }

    }
}
