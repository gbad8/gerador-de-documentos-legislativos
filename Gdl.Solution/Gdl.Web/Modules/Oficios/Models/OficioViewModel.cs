using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Oficios.Models
{
    public class OficioViewModel
    {
        public int Id { get; set; }

        public string? Numero { get; set; }

        [Required(ErrorMessage = "O Assunto é obrigatório.")]
        [StringLength(500)]
        [Display(Name = "Assunto")]
        public string Assunto { get; set; } = string.Empty;

        [Required(ErrorMessage = "O Corpo do ofício é obrigatório.")]
        [Display(Name = "Corpo do Ofício")]
        public string Corpo { get; set; } = string.Empty;

        [Required(ErrorMessage = "A Data é obrigatória.")]
        [DataType(DataType.Date)]
        public DateTime Data { get; set; } = DateTime.Today;

        [Display(Name = "Ofício Conjunto")]
        public bool EConjunto { get; set; }

        [Required(ErrorMessage = "O Destinatário é obrigatório.")]
        [StringLength(200)]
        [Display(Name = "Destinatário")]
        public string DestinatarioNome { get; set; } = string.Empty;

        [StringLength(200)]
        [Display(Name = "Cargo")]
        public string? DestinatarioCargo { get; set; }

        [StringLength(200)]
        [Display(Name = "Órgão")]
        public string? DestinatarioOrgao { get; set; }

        [Display(Name = "Endereço")]
        public string? DestinatarioEndereco { get; set; }

        [Required(ErrorMessage = "O Pronome de tratamento é obrigatório.")]
        [StringLength(50)]
        [Display(Name = "Pronome de tratamento")]
        public string DestinatarioPronome { get; set; } = "Ao Senhor(a)";

        [Required(ErrorMessage = "Selecione o Autor Principal.")]
        [Display(Name = "Autor Principal")]
        public int AutorId { get; set; }

        [Display(Name = "Órgão Emissor")]
        public int? OrgaoId { get; set; }

        [Display(Name = "Coautores")]
        public List<int> CoautoresIds { get; set; } = new List<int>();
    }
}
