using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Http;
using Gdl.Web.Modules.Camaras.Models;
using Gdl.Web.Modules.Camaras.Models.Enums;

namespace Gdl.Web.Modules.Camaras.Models
{
    public class CamaraViewModel
    {
        public int Id { get; set; }

        [Required(ErrorMessage = "O Nome da Instituição é obrigatório.")]
        [StringLength(200)]
        [Display(Name = "Nome da Instituição *")]
        public string Nome { get; set; } = string.Empty;

        [StringLength(100)]
        public string? Cidade { get; set; }

        [Required(ErrorMessage = "O Estado é obrigatório.")]
        [Display(Name = "Estado *")]
        public EstadoCamara Estado { get; set; }

        [Required(ErrorMessage = "O CNPJ é obrigatório.")]
        [StringLength(20)]
        [Display(Name = "CNPJ *")]
        public string Cnpj { get; set; } = string.Empty;

        [StringLength(20)]
        public string? Telefone { get; set; }

        [EmailAddress(ErrorMessage = "E-mail inválido.")]
        [StringLength(254)]
        [Display(Name = "E-mail")]
        public string? Email { get; set; }

        [StringLength(10)]
        public string? Cep { get; set; }

        [Required(ErrorMessage = "O Endereço Completo é obrigatório.")]
        [Display(Name = "Endereço Completo *")]
        public string Endereco { get; set; } = string.Empty;

        public string? LogomarcaBase64 { get; set; }

        [Display(Name = "Atualizar Logotipo")]
        public IFormFile? UploadLogomarca { get; set; }
    }
}
