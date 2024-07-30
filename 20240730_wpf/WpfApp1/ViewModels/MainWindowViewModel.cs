using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WpfApp1.Models;

namespace WpfApp1.ViewModels
{
    public class MainWindowViewModel : Bases.ViewModelBase
    {
        private IList<bool>? _genderTypes = new List<bool>() { true, false };
        public IList<bool>? GenderTypes
        {
            get => _genderTypes;
        }
        private IList<Person>? _people;
        public IList<Person>? People
        {
            get => _people;
            set => SetProperty(ref _people, value);
        }

        private Person? _selectedPerson;
        public Person? SelectedPerson
        {
            get => _selectedPerson;
            set => SetProperty(ref _selectedPerson, value);
        }

        public MainWindowViewModel()
        {
            People = new List<Person>
            {
                new Person{Id = 119302, Name = "김정현", Gender = true},
                new Person{Id = 119801, Name = "이현재", Gender = true},
                new Person{Id = 111202, Name = "송정환", Gender = true},
                new Person{Id = 111319, Name = "이보현", Gender = true},
                new Person{Id = 112215, Name = "고진욱", Gender = true},
                new Person{Id = 112221, Name = "황보아", Gender = true},
                new Person{Id = 200111, Name = "김푸름", Gender = true},
                new Person{Id = 112113, Name = "백아인", Gender = true},
                new Person{Id = 112109, Name = "신소현", Gender = false},
                new Person{Id = 112206, Name = "주명길", Gender = true},
            };
        }

    }
}
