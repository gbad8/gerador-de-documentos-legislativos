using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Orgaos.Models
{
    public class OrgaoViewModel
    {
        public int Id { get; set; }

        [Required(ErrorMessage = "O Nome do Órgão é obrigatório.")]
        [StringLength(100)]
        [Display(Name = "Nome do Órgão *")]
        public string Nome { get; set; } = string.Empty;

        [StringLength(10, ErrorMessage = "A abreviatura deve ter no máximo 10 caracteres.")]
        [Display(Name = "Abreviatura / Sigla")]
        public string? Abreviatura { get; set; }
    }
}
