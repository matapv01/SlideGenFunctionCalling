import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AppLayout } from "@/components/AppLayout";
import { Crown, Zap, Gift } from "lucide-react";

interface SubscriptionInfo {
  tier: string;
  is_active: boolean;
  expires_at?: string;
  daily_limits: {
    idea_generation: number;
    docx_upload: number;
    max_docx_slides: number;
  };
  current_usage: {
    idea_generation: number;
    docx_upload: number;
  };
  usage_reset_date: string;
}

interface PricingTier {
  name: string;
  display_name: string;
  price: number;
  currency: string;
  period: string;
  features: Record<string, any>;
}

const Subscription = () => {
  const { isAuthenticated } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [subscriptionInfo, setSubscriptionInfo] = useState<SubscriptionInfo | null>(null);
  const [pricingTiers, setPricingTiers] = useState<PricingTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [codeInput, setCodeInput] = useState("");
  const [redeemingCode, setRedeemingCode] = useState(false);
  const [codeDialogOpen, setCodeDialogOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    loadSubscriptionData();
  }, [isAuthenticated, navigate]);

  const loadSubscriptionData = async () => {
    try {
      const [subInfo, pricingInfo] = await Promise.all([
        api.getSubscriptionInfo(),
        api.getPricingInfo()
      ]);
      setSubscriptionInfo(subInfo);
      setPricingTiers(pricingInfo.tiers);
    } catch (error: any) {
      toast({
        title: t.subscription_error_load_title,
        description: error.message || t.subscription_error_retry_later,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRedeemCode = async () => {
    if (!codeInput.trim()) {
      toast({
        title: t.subscription_error_code_required,
        variant: "destructive"
      });
      return;
    }

    setRedeemingCode(true);
    try {
      const result = await api.redeemCode(codeInput);
      toast({
        title: t.subscription_success_title,
        description: result.message
      });
      setCodeDialogOpen(false);
      setCodeInput("");
      await loadSubscriptionData();
    } catch (error: any) {
      toast({
        title: t.subscription_error_redeem_title,
        description: error.message || t.subscription_error_invalid_code,
        variant: "destructive"
      });
    } finally {
      setRedeemingCode(false);
    }
  };

  const handleUpgrade = async (tier: string) => {
    try {
      await api.upgradeSubscription(tier);
    } catch (error: any) {
      toast({
        title: t.subscription_error_upgrade_title,
        description: t.subscription_error_upgrade_desc,
        variant: "destructive"
      });
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case "plus": return <Zap className="h-5 w-5 text-blue-500" />;
      case "ultra": return <Crown className="h-5 w-5 text-purple-500" />;
      default: return <Gift className="h-5 w-5 text-green-500" />;
    }
  };

  const getTierBadgeVariant = (tier: string) => {
    switch (tier.toLowerCase()) {
      case "plus": return "default";
      case "ultra": return "secondary";
      default: return "outline";
    }
  };

  const formatLimit = (value: number): string => {
    return value === -1 ? t.subscription_unlimited : value.toString();
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    );
  }

  if (!subscriptionInfo) {
    return (
      <AppLayout>
        <div className="container mx-auto p-6">
          <Card>
            <CardContent className="text-center p-6">
              <p>{t.subscription_error_load_info}</p>
              <Button onClick={loadSubscriptionData} className="mt-4">{t.subscription_retry}</Button>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="container mx-auto p-6 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold">{t.subscription_title}</h1>
          <p className="text-muted-foreground">{t.subscription_subtitle}</p>
        </div>

        {/* Current Subscription */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getTierIcon(subscriptionInfo.tier)}
              {t.subscription_current_plan}: {subscriptionInfo.tier.toUpperCase()}
              <Badge variant={getTierBadgeVariant(subscriptionInfo.tier)} className={subscriptionInfo.is_active ? "bg-green-500 text-white hover:bg-green-600 border-transparent" : ""}>
                {subscriptionInfo.is_active ? t.subscription_active : t.subscription_expired}
              </Badge>
            </CardTitle>
            <CardDescription>
              {subscriptionInfo.expires_at
                ? `${t.subscription_expires_at}: ${new Date(subscriptionInfo.expires_at).toLocaleDateString()}`
                : t.subscription_no_expiry}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">{t.subscription_idea_generation}</Label>
                <div className="text-lg font-semibold">
                  {subscriptionInfo.current_usage.idea_generation} / {formatLimit(subscriptionInfo.daily_limits.idea_generation)} {t.subscription_today}
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">{t.subscription_docx_upload}</Label>
                <div className="text-lg font-semibold">
                  {subscriptionInfo.current_usage.docx_upload} / {formatLimit(subscriptionInfo.daily_limits.docx_upload)} {t.subscription_today}
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">{t.subscription_slide_limit}</Label>
                <div className="text-lg font-semibold">
                  {formatLimit(subscriptionInfo.daily_limits.max_docx_slides)} {t.subscription_slides}
                </div>
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <Dialog open={codeDialogOpen} onOpenChange={setCodeDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Gift className="h-4 w-4 mr-2" />
                    {t.subscription_redeem_code}
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{t.subscription_enter_code}</DialogTitle>
                    <DialogDescription>
                      {t.subscription_enter_code_desc}
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="code">{t.subscription_code_label}</Label>
                      <Input
                        id="code"
                        value={codeInput}
                        onChange={(e) => setCodeInput(e.target.value)}
                        placeholder={t.subscription_code_placeholder}
                        className="uppercase"
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleRedeemCode} disabled={redeemingCode} className="flex-1">
                        {redeemingCode ? t.subscription_processing : t.subscription_use_code}
                      </Button>
                      <Button variant="outline" onClick={() => setCodeDialogOpen(false)}>
                        {t.subscription_cancel}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardContent>
        </Card>

        {/* Pricing Tiers */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {pricingTiers.map((tier) => (
            <Card key={tier.name} className={`relative ${subscriptionInfo.tier === tier.name ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-950/30' : ''}`}>
              {subscriptionInfo.tier === tier.name && (
                <div className="absolute -top-3 left-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  {t.subscription_current_tier}
                </div>
              )}
              <CardHeader className="text-center">
                <div className="flex justify-center mb-2">
                  {getTierIcon(tier.name)}
                </div>
                <CardTitle className="text-2xl">{tier.display_name}</CardTitle>
                <CardDescription>
                  <span className="text-3xl font-bold">${tier.price}</span>
                  {tier.period !== "forever" && <span className="text-muted-foreground">/{tier.period}</span>}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">{t.subscription_idea_generation}</span>
                    <span className="font-medium">{tier.features.idea_generation}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">{t.subscription_docx_upload}</span>
                    <span className="font-medium">{tier.features.docx_upload}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">{t.subscription_slide_limit}</span>
                    <span className="font-medium">{tier.features.max_slides}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">{t.subscription_content_length}</span>
                    <span className="font-medium">{tier.features.content_length}</span>
                  </div>
                  {tier.features.priority_support && (
                    <div className="flex justify-between">
                      <span className="text-sm">{t.subscription_priority_support}</span>
                      <span className="font-medium text-green-600">✓</span>
                    </div>
                  )}
                  {tier.features.advanced_features && (
                    <div className="flex justify-between">
                      <span className="text-sm">{t.subscription_advanced_features}</span>
                      <span className="font-medium text-green-600">✓</span>
                    </div>
                  )}
                </div>

                {subscriptionInfo.tier !== tier.name && tier.name !== "free" && (
                  <Button
                    className="w-full"
                    onClick={() => handleUpgrade(tier.name)}
                    variant={tier.name === "ultra" ? "default" : "outline"}
                  >
                    {t.subscription_upgrade}
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{t.subscription_guide_title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">• {t.subscription_guide_code_only}</p>
            <p className="text-sm text-muted-foreground">
              • {t.subscription_guide_free_ultra}: <code className="bg-muted px-2 py-1 rounded">SLIDEGENIUS</code>
            </p>
            <p className="text-sm text-muted-foreground">• {t.subscription_guide_payment_soon}</p>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
};

export default Subscription;
