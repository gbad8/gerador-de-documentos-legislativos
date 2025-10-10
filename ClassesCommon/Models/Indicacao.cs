using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

// #pragma warning disable IDE0130 // Namespace does not match folder structure
namespace ClassesCommon.Models
// #pragma warning restore IDE0130 // Namespace does not match folder structure
{
    public class Indicacao
    {
        public int LetterNumber { get; set; }
        public DateOnly ApprovalDate { get; set; }
        public int PropositionNumber { get; set; }
        public string Subject { get; set; } = string.Empty;
        public string Request { get; set; } = string.Empty;
        public bool IsJoint { get; set; }
        public string AuthorName { get; set; }  = string.Empty;
        public string ApprovalQuorum { get; set; } = string.Empty;
        public int SessionNumber { get; set; }

        public void PrintPdf()
        {
            Console.WriteLine($"A Indicação n°{PropositionNumber} foi aprovada!");
        }
    }
}