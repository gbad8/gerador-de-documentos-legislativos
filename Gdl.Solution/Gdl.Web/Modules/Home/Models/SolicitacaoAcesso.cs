using System;
using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Home.Models
{
    public class SolicitacaoAcesso
    {
        public int Id { get; set; }

        [Required, MaxLength(100)]
        public string NomeCamara { get; set; } = string.Empty;

        [Required, MaxLength(2)]
        public string Estado { get; set; } = string.Empty;

        [Required, MaxLength(20)]
        public string Telefone { get; set; } = string.Empty;

        [Required, MaxLength(100), EmailAddress]
        public string Email { get; set; } = string.Empty;

        public StatusSolicitacao Status { get; set; } = StatusSolicitacao.Pendente;

        public DateTime DataSolicitacao { get; set; } = DateTime.UtcNow;
    }

    public enum StatusSolicitacao
    {
        Pendente,
        Aprovada,
        Rejeitada
    }
}
